"""Pruebas HTTP de la consulta de disponibilidad de un intervalo.

Cubren los escenarios de
``openspec/changes/c11-disponibilidad-intervalo/specs/appointment-api/spec.md``
para la nueva operacion: intervalo libre, intervalo ocupado por profesional o
por sillon, turno cancelado que no bloquea, intervalo invalido, recurso ausente
o ajeno al consultorio y sillon obligatorio.
"""

import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from src.api.dependencies import get_repository
from src.api.main import create_app
from src.appointments import AppointmentRepository


def _local_time(hour: int, minute: int = 0) -> datetime:
    """Hora de Buenos Aires, que el dominio normaliza a UTC."""
    return datetime(2026, 10, 15, hour, minute, tzinfo=timezone(timedelta(hours=-3)))


def _utc_time(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 10, 15, hour, minute, tzinfo=timezone.utc)


class AvailabilityApiTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.repository = AppointmentRepository(
            Path(temporary_directory.name) / "appointments.sqlite3"
        )
        self.repository.register_clinic(
            "C1", "America/Argentina/Buenos_Aires", manages_chairs=True
        )
        self.repository.register_professional("C1", "P1")
        self.repository.register_professional("C1", "P2")
        self.repository.register_chair("C1", "S1")
        self.repository.register_chair("C1", "S2")
        self.repository.register_patient("C1", "patient-1")
        self.repository.register_service("C1", "consulta")

        self.app = create_app()
        self.app.dependency_overrides[get_repository] = lambda: self.repository
        self.addCleanup(self.app.dependency_overrides.clear)
        self.client = TestClient(self.app)

    def _create(
        self,
        *,
        professional_id: str = "P1",
        chair_id: str | None = "S1",
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ):
        return self.repository.create_appointment(
            clinic_id="C1",
            professional_id=professional_id,
            chair_id=chair_id,
            patient_id="patient-1",
            service_id="consulta",
            start_at=start_at or _local_time(9),
            end_at=end_at or _local_time(9, 30),
        )

    def _query(
        self,
        *,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        professional_id: str = "P1",
        chair_id: str | None = "S1",
    ) -> dict:
        parameters = {
            "start_at": (start_at or _local_time(9)).isoformat(),
            "end_at": (end_at or _local_time(9, 30)).isoformat(),
            "professional_id": professional_id,
        }
        if chair_id is not None:
            parameters["chair_id"] = chair_id
        response = self.client.get("/clinics/C1/availability", params=parameters)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_reports_a_free_interval(self) -> None:
        body = self._query()

        self.assertTrue(body["available"])
        self.assertIsNone(body["conflicting_resource"])
        self.assertEqual(body["clinic_id"], "C1")
        self.assertEqual(body["professional_id"], "P1")
        self.assertEqual(body["chair_id"], "S1")
        self.assertEqual(
            datetime.fromisoformat(body["start_at"]), _utc_time(12)
        )
        self.assertEqual(
            datetime.fromisoformat(body["end_at"]), _utc_time(12, 30)
        )

    def test_reports_the_professional_as_the_conflicting_resource(self) -> None:
        self._create()

        body = self._query()

        self.assertFalse(body["available"])
        self.assertEqual(body["conflicting_resource"], "professional")

    def test_reports_the_chair_as_the_conflicting_resource(self) -> None:
        self._create()

        body = self._query(professional_id="P2")

        self.assertFalse(body["available"])
        self.assertEqual(body["conflicting_resource"], "chair")

    def test_a_cancelled_appointment_does_not_block_the_interval(self) -> None:
        appointment = self._create()
        self.repository.cancel_appointment(
            clinic_id="C1", appointment_id=appointment.id
        )

        body = self._query()

        self.assertTrue(body["available"])
        self.assertIsNone(body["conflicting_resource"])

    def test_the_response_does_not_disclose_the_patient_of_the_conflict(self) -> None:
        self._create()

        response = self.client.get(
            "/clinics/C1/availability",
            params={
                "start_at": _local_time(9).isoformat(),
                "end_at": _local_time(9, 30).isoformat(),
                "professional_id": "P1",
                "chair_id": "S1",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("patient-1", response.text)
        self.assertNotIn("patient", response.text.lower())

    def test_rejects_an_inverted_interval(self) -> None:
        response = self.client.get(
            "/clinics/C1/availability",
            params={
                "start_at": _local_time(10).isoformat(),
                "end_at": _local_time(9).isoformat(),
                "professional_id": "P1",
                "chair_id": "S1",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "invalid_appointment_interval")

    def test_rejects_an_interval_without_timezone(self) -> None:
        response = self.client.get(
            "/clinics/C1/availability",
            params={
                "start_at": "2026-10-15T09:00:00",
                "end_at": "2026-10-15T09:30:00",
                "professional_id": "P1",
                "chair_id": "S1",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "invalid_appointment_interval")

    def test_rejects_an_unknown_professional(self) -> None:
        response = self.client.get(
            "/clinics/C1/availability",
            params={
                "start_at": _local_time(9).isoformat(),
                "end_at": _local_time(9, 30).isoformat(),
                "professional_id": "P9",
                "chair_id": "S1",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "resource_unavailable")

    def test_rejects_an_unknown_clinic(self) -> None:
        response = self.client.get(
            "/clinics/C9/availability",
            params={
                "start_at": _local_time(9).isoformat(),
                "end_at": _local_time(9, 30).isoformat(),
                "professional_id": "P1",
                "chair_id": "S1",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "resource_unavailable")

    def test_requires_a_chair_when_the_clinic_manages_chairs(self) -> None:
        response = self.client.get(
            "/clinics/C1/availability",
            params={
                "start_at": _local_time(9).isoformat(),
                "end_at": _local_time(9, 30).isoformat(),
                "professional_id": "P1",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "chair_required")

    def test_rejects_a_missing_required_parameter(self) -> None:
        response = self.client.get(
            "/clinics/C1/availability",
            params={"start_at": _local_time(9).isoformat()},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], "invalid_request")

    def test_the_query_does_not_create_or_modify_appointments(self) -> None:
        self._create()
        before = self.repository.count_appointments(clinic_id="C1")

        self._query()

        self.assertEqual(self.repository.count_appointments(clinic_id="C1"), before)


if __name__ == "__main__":
    unittest.main()
