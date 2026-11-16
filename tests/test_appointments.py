from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from threading import Barrier
import unittest

from src.appointments import (
    AppointmentConflict,
    AppointmentRepository,
    ChairRequired,
    InvalidAppointmentInterval,
    ResourceUnavailable,
)


class AppointmentRepositoryTests(unittest.TestCase):
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

    def test_creates_an_appointment_for_available_resources(self) -> None:
        appointment = self._create()

        self.assertEqual(appointment.status, "scheduled")
        self.assertEqual(appointment.professional_id, "P1")
        self.assertEqual(appointment.chair_id, "S1")
        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 1)

    def test_rejects_professional_overlap_without_mutation_or_patient_disclosure(self) -> None:
        existing = self._create()
        self._set_status(existing.id, "confirmed")
        existing = self.repository.get_appointment(
            clinic_id="C1", appointment_id=existing.id
        )
        self.repository.register_patient("C1", "private-patient-marker")

        with self.assertRaises(AppointmentConflict) as raised:
            self._create(
                professional_id="P1",
                chair_id="S2",
                start_at=self._time(9, 15),
                end_at=self._time(9, 45),
                patient_id="private-patient-marker",
            )

        self.assertEqual(raised.exception.resource, "professional")
        self.assertNotIn("patient-1", str(raised.exception))
        self.assertNotIn("private-patient-marker", str(raised.exception))
        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 1)
        self.assertEqual(
            self.repository.get_appointment(
                clinic_id="C1", appointment_id=existing.id
            ),
            existing,
        )

    def test_rejects_chair_overlap_with_another_professional(self) -> None:
        self._create()

        with self.assertRaises(AppointmentConflict) as raised:
            self._create(
                professional_id="P2",
                chair_id="S1",
                start_at=self._time(9, 15),
                end_at=self._time(9, 45),
                patient_id="patient-2",
            )

        self.assertEqual(raised.exception.resource, "chair")
        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 1)

    def test_allows_adjacent_appointments_on_same_resources(self) -> None:
        first = self._create()
        second = self._create(
            start_at=self._time(9, 30),
            end_at=self._time(10),
            patient_id="patient-2",
        )

        self.assertEqual(first.end_at, second.start_at)
        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 2)

    def test_cancelled_appointment_releases_its_resources(self) -> None:
        cancelled = self._create()
        self.repository.cancel_appointment(
            clinic_id="C1", appointment_id=cancelled.id
        )

        replacement = self._create(patient_id="patient-2")

        self.assertNotEqual(cancelled.id, replacement.id)
        self.assertEqual(replacement.status, "scheduled")
        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 2)

    def test_rejects_empty_or_inverted_interval_as_validation_error(self) -> None:
        with self.assertRaises(InvalidAppointmentInterval):
            self._create(start_at=self._time(9), end_at=self._time(9))
        with self.assertRaises(InvalidAppointmentInterval):
            self._create(start_at=self._time(10), end_at=self._time(9))

        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 0)

    def test_rejects_naive_datetime(self) -> None:
        with self.assertRaises(InvalidAppointmentInterval):
            self._create(
                start_at=datetime(2026, 10, 15, 9),
                end_at=self._time(9, 30),
            )

    def test_does_not_conflict_with_same_resource_ids_in_another_clinic(self) -> None:
        self._create()
        self._register_clinic("C2", manages_chairs=True)
        self.repository.register_professional("C2", "P1")
        self.repository.register_chair("C2", "S1")
        self.repository.register_patient("C2", "patient-1")
        self.repository.register_service("C2", "exam")

        other_clinic_appointment = self.repository.create_appointment(
            clinic_id="C2",
            professional_id="P1",
            chair_id="S1",
            patient_id="patient-1",
            service_id="exam",
            start_at=self._time(9),
            end_at=self._time(9, 30),
        )

        self.assertEqual(other_clinic_appointment.clinic_id, "C2")
        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 1)
        self.assertEqual(self.repository.count_appointments(clinic_id="C2"), 1)

    def test_rejects_resources_from_another_clinic(self) -> None:
        self._register_clinic("C2", manages_chairs=False)

        with self.assertRaises(ResourceUnavailable):
            self.repository.create_appointment(
                clinic_id="C2",
                professional_id="P1",
                patient_id="patient-1",
                service_id="exam",
                start_at=self._time(9),
                end_at=self._time(9, 30),
            )

    def test_chair_is_required_when_clinic_manages_chairs(self) -> None:
        with self.assertRaises(ChairRequired):
            self._create(chair_id=None)

        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 0)

    def test_rejects_inactive_chair(self) -> None:
        self.repository.register_chair("C1", "S3", active=False)

        with self.assertRaises(ResourceUnavailable):
            self._create(chair_id="S3")

        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 0)

    def test_clinic_without_chair_management_can_book_without_a_chair(self) -> None:
        self._register_clinic("C2", manages_chairs=False)
        self.repository.register_professional("C2", "P1")
        self.repository.register_patient("C2", "patient-1")
        self.repository.register_service("C2", "exam")

        appointment = self.repository.create_appointment(
            clinic_id="C2",
            professional_id="P1",
            patient_id="patient-1",
            service_id="exam",
            start_at=self._time(9),
            end_at=self._time(9, 30),
        )

        self.assertIsNone(appointment.chair_id)

    def test_reschedule_excludes_itself_and_rejects_other_active_conflicts(self) -> None:
        original = self._create()
        moved = self.repository.reschedule_appointment(
            clinic_id="C1",
            appointment_id=original.id,
            start_at=self._time(10),
            end_at=self._time(10, 30),
        )
        self.assertEqual(moved.start_at, self._time(10).astimezone(moved.start_at.tzinfo))

        self._create(
            start_at=self._time(11),
            end_at=self._time(11, 30),
            patient_id="patient-2",
        )
        with self.assertRaises(AppointmentConflict):
            self.repository.reschedule_appointment(
                clinic_id="C1",
                appointment_id=original.id,
                start_at=self._time(11, 15),
                end_at=self._time(11, 45),
            )
        unchanged = self.repository.get_appointment(
            clinic_id="C1", appointment_id=original.id
        )
        self.assertEqual(unchanged.start_at, moved.start_at)

    def test_normalizes_local_argentina_times_to_utc(self) -> None:
        appointment = self._create()

        self.assertEqual(appointment.start_at.utcoffset().total_seconds(), 0)
        self.assertEqual(appointment.start_at.hour, 12)
        self.assertEqual(
            appointment.end_at,
            self._time(9, 30).astimezone(appointment.end_at.tzinfo),
        )

    def test_only_scheduled_and_confirmed_appointments_block_resources(self) -> None:
        appointment = self._create()
        with self.repository._transaction() as connection:
            connection.execute(
                "UPDATE appointments SET status = 'completed' WHERE id = ?",
                (appointment.id,),
            )

        replacement = self._create(patient_id="patient-2")

        self.assertEqual(replacement.status, "scheduled")

    def test_concurrent_requests_cannot_book_the_same_resources(self) -> None:
        barrier = Barrier(2)

        def attempt(patient_id: str) -> str:
            barrier.wait()
            try:
                self._create(patient_id=patient_id)
                return "created"
            except AppointmentConflict:
                return "conflict"

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(attempt, ("patient-1", "patient-2"))
            )

        self.assertCountEqual(results, ["created", "conflict"])
        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 1)

    def test_concurrent_professionals_cannot_book_the_same_chair(self) -> None:
        barrier = Barrier(2)

        def attempt(professional_id: str, patient_id: str) -> str:
            barrier.wait()
            try:
                self._create(
                    professional_id=professional_id,
                    patient_id=patient_id,
                )
                return "created"
            except AppointmentConflict:
                return "conflict"

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    lambda values: attempt(*values),
                    (("P1", "patient-1"), ("P2", "patient-2")),
                )
            )

        self.assertCountEqual(results, ["created", "conflict"])
        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), 1)

    def test_concurrent_reschedules_cannot_double_book_resources(self) -> None:
        first = self._create()
        second = self._create(
            start_at=self._time(10),
            end_at=self._time(10, 30),
            patient_id="patient-2",
        )
        barrier = Barrier(2)

        def attempt(appointment_id: str) -> str:
            barrier.wait()
            try:
                self.repository.reschedule_appointment(
                    clinic_id="C1",
                    appointment_id=appointment_id,
                    start_at=self._time(11),
                    end_at=self._time(11, 30),
                )
                return "rescheduled"
            except AppointmentConflict:
                return "conflict"

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(attempt, (first.id, second.id)))

        self.assertCountEqual(results, ["rescheduled", "conflict"])
        appointments = (
            self.repository.get_appointment(clinic_id="C1", appointment_id=first.id),
            self.repository.get_appointment(clinic_id="C1", appointment_id=second.id),
        )
        self.assertEqual(
            sum(appointment.start_at == self._time(11).astimezone(timezone.utc)
                for appointment in appointments),
            1,
        )


if __name__ == "__main__":
    unittest.main()
