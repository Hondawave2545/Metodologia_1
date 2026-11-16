"""Pruebas de la consulta de disponibilidad en el dominio.

La disponibilidad la decide la misma regla de solapamientos que usa el alta,
por lo que estas pruebas fijan la semántica que el dominio ya tiene: intervalos
semiabiertos ``[inicio, fin)`` y solo ``scheduled`` y ``confirmed`` bloqueando.
"""

from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from src.appointments import (
    AppointmentRepository,
    ChairRequired,
    InvalidAppointmentInterval,
    ResourceUnavailable,
)


class AvailabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.repository = AppointmentRepository(
            Path(self.temporary_directory.name) / "appointments.sqlite3"
        )
        self._register_clinic("C1", manages_chairs=True)
        self.repository.register_professional("C1", "P1")
        self.repository.register_professional("C1", "P2")
        self.repository.register_chair("C1", "S1")
        self.repository.register_chair("C1", "S2")
        self.repository.register_patient("C1", "patient-1")
        self.repository.register_patient("C1", "patient-2")
        self.repository.register_service("C1", "exam")

    def _register_clinic(self, clinic_id: str, *, manages_chairs: bool) -> None:
        self.repository.register_clinic(
            clinic_id,
            "America/Argentina/Buenos_Aires",
            manages_chairs=manages_chairs,
        )

    def _set_status(self, appointment_id: str, status: str) -> None:
        with closing(sqlite3.connect(self.repository.database_path)) as connection:
            connection.execute(
                "UPDATE appointments SET status = ? WHERE id = ?",
                (status, appointment_id),
            )
            connection.commit()

    @staticmethod
    def _time(hour: int, minute: int = 0) -> datetime:
        return datetime(
            2026,
            10,
            15,
            hour,
            minute,
            tzinfo=timezone(timedelta(hours=-3)),
        )

    def _create(
        self,
        *,
        professional_id: str = "P1",
        chair_id: str | None = "S1",
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        patient_id: str = "patient-1",
    ):
        return self.repository.create_appointment(
            clinic_id="C1",
            professional_id=professional_id,
            chair_id=chair_id,
            patient_id=patient_id,
            service_id="exam",
            start_at=start_at or self._time(9),
            end_at=end_at or self._time(9, 30),
        )

    def _availability(
        self,
        *,
        clinic_id: str = "C1",
        professional_id: str = "P1",
        chair_id: str | None = "S1",
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> str | None:
        return self.repository.check_availability(
            clinic_id=clinic_id,
            professional_id=professional_id,
            chair_id=chair_id,
            start_at=start_at or self._time(9),
            end_at=end_at or self._time(9, 30),
        )

    def test_reports_a_free_interval(self) -> None:
        self.assertIsNone(self._availability())

    def test_reports_the_professional_as_the_conflicting_resource(self) -> None:
        self._create()

        self.assertEqual(self._availability(), "professional")

    def test_reports_the_chair_as_the_conflicting_resource(self) -> None:
        self._create()

        self.assertEqual(
            self._availability(professional_id="P2", chair_id="S1"),
            "chair",
        )

    def test_a_cancelled_appointment_does_not_block_the_interval(self) -> None:
        appointment = self._create()
        self.repository.cancel_appointment(
            clinic_id="C1", appointment_id=appointment.id
        )

        self.assertIsNone(self._availability())

    def test_only_scheduled_and_confirmed_appointments_block_resources(self) -> None:
        appointment = self._create()
        self._set_status(appointment.id, "completed")

        self.assertIsNone(self._availability())

    def test_allows_the_interval_that_touches_an_existing_one(self) -> None:
        self._create()

        self.assertIsNone(
            self._availability(
                start_at=self._time(9, 30),
                end_at=self._time(10),
            )
        )

    def test_rejects_an_inverted_interval(self) -> None:
        with self.assertRaises(InvalidAppointmentInterval):
            self._availability(start_at=self._time(10), end_at=self._time(9))

    def test_rejects_a_naive_datetime(self) -> None:
        with self.assertRaises(InvalidAppointmentInterval):
            self._availability(
                start_at=datetime(2026, 10, 15, 9),
                end_at=self._time(9, 30),
            )

    def test_rejects_an_unknown_clinic(self) -> None:
        with self.assertRaises(ResourceUnavailable):
            self._availability(clinic_id="C9")

    def test_rejects_an_inactive_professional(self) -> None:
        self.repository.register_professional("C1", "P3", active=False)

        with self.assertRaises(ResourceUnavailable):
            self._availability(professional_id="P3")

    def test_rejects_a_professional_from_another_clinic(self) -> None:
        self._register_clinic("C2", manages_chairs=True)

        with self.assertRaises(ResourceUnavailable):
            self._availability(clinic_id="C2", professional_id="P1")

    def test_rejects_an_inactive_chair(self) -> None:
        self.repository.register_chair("C1", "S3", active=False)

        with self.assertRaises(ResourceUnavailable):
            self._availability(chair_id="S3")

    def test_requires_a_chair_when_the_clinic_manages_chairs(self) -> None:
        with self.assertRaises(ChairRequired):
            self._availability(chair_id=None)

    def test_allows_a_clinic_without_chair_management_to_check_without_a_chair(
        self,
    ) -> None:
        self._register_clinic("C2", manages_chairs=False)
        self.repository.register_professional("C2", "P1")

        self.assertIsNone(
            self._availability(clinic_id="C2", professional_id="P1", chair_id=None)
        )

    def test_does_not_conflict_with_same_resource_ids_in_another_clinic(self) -> None:
        self._register_clinic("C2", manages_chairs=True)
        self.repository.register_professional("C2", "P1")
        self.repository.register_chair("C2", "S1")
        self.repository.register_patient("C2", "patient-1")
        self.repository.register_service("C2", "exam")
        self.repository.create_appointment(
            clinic_id="C2",
            professional_id="P1",
            chair_id="S1",
            patient_id="patient-1",
            service_id="exam",
            start_at=self._time(9),
            end_at=self._time(9, 30),
        )

        self.assertIsNone(self._availability())


if __name__ == "__main__":
    unittest.main()
