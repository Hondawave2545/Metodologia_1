"""Pruebas HTTP de las cuatro operaciones de la API de turnos.

Cubren los escenarios de
``openspec/changes/c10-api-turnos-swagger/specs/appointment-api/spec.md``
para crear, consultar, reprogramar y cancelar, y los casos limite de
conflictos, validacion, aislamiento por consultorio y no divulgacion de datos
del paciente.
"""

import sqlite3
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


class AppointmentApiTestCase(unittest.TestCase):
    """Base con el consultorio de prueba, compartido por los dos grupos de pruebas."""

    def setUp(self) -> None:
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.repository = AppointmentRepository(
            Path(temporary_directory.name) / "appointments.sqlite3"
        )
        self._register_clinic("C1")
        self._register_clinic("C2")
        self.repository.register_professional("C1", "P1")
        self.repository.register_professional("C1", "P2")
        self.repository.register_chair("C1", "S1")
        self.repository.register_chair("C1", "S2")
        self.repository.register_chair("C1", "S3")
        self.repository.register_patient("C1", "patient-1")
        self.repository.register_patient("C1", "patient-2")
        self.repository.register_service("C1", "consulta")
        # Mismos identificadores en otro consultorio: no deben interferir.
        self.repository.register_professional("C2", "P1")
        self.repository.register_chair("C2", "S1")
        self.repository.register_patient("C2", "patient-1")
        self.repository.register_service("C2", "consulta")

        self.app = create_app()
        self.app.dependency_overrides[get_repository] = lambda: self.repository
        self.addCleanup(self.app.dependency_overrides.clear)
        self.client = TestClient(self.app)

    def _register_clinic(self, clinic_id: str) -> None:
        self.repository.register_clinic(
            clinic_id, "America/Argentina/Buenos_Aires", manages_chairs=True
        )

    def _deactivate_chair(self, clinic_id: str, chair_id: str) -> None:
        with closing(sqlite3.connect(self.repository.database_path)) as connection:
            connection.execute(
                "UPDATE chairs SET active = 0 WHERE clinic_id = ? AND id = ?",
                (clinic_id, chair_id),
            )
            connection.commit()

    def _payload(self, **overrides: object) -> dict:
        payload = {
            "professional_id": "P1",
            "patient_id": "patient-1",
            "service_id": "consulta",
            "chair_id": "S1",
            "start_at": _local_time(9).isoformat(),
            "end_at": _local_time(9, 30).isoformat(),
        }
        payload.update(overrides)
        return payload

    def _create(self, clinic_id: str = "C1", **overrides: object) -> dict:
        response = self.client.post(
            f"/clinics/{clinic_id}/appointments", json=self._payload(**overrides)
        )
        self.assertEqual(201, response.status_code, response.text)
        return response.json()


class AppointmentApiTests(AppointmentApiTestCase):
    """Las cuatro operaciones del contrato HTTP."""

    def test_creating_an_appointment_returns_the_created_appointment(self):
        body = self._create()

        self.assertTrue(body["id"])
        self.assertEqual("C1", body["clinic_id"])
        self.assertEqual("P1", body["professional_id"])
        self.assertEqual("S1", body["chair_id"])
        self.assertEqual("patient-1", body["patient_id"])
        self.assertEqual("consulta", body["service_id"])
        self.assertEqual("scheduled", body["status"])
        self.assertEqual(_utc_time(12), datetime.fromisoformat(body["start_at"]))
        self.assertEqual(_utc_time(12, 30), datetime.fromisoformat(body["end_at"]))

    def test_querying_the_appointment_returns_the_same_data(self):
        created = self._create()

        response = self.client.get(f"/clinics/C1/appointments/{created['id']}")

        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual(created, response.json())

    def test_rescheduling_updates_the_interval(self):
        created = self._create()

        response = self.client.patch(
            f"/clinics/C1/appointments/{created['id']}",
            json={
                "start_at": _local_time(11).isoformat(),
                "end_at": _local_time(11, 30).isoformat(),
            },
        )

        self.assertEqual(200, response.status_code, response.text)
        body = response.json()
        self.assertEqual(created["id"], body["id"])
        self.assertEqual(_utc_time(14), datetime.fromisoformat(body["start_at"]))
        self.assertEqual(_utc_time(14, 30), datetime.fromisoformat(body["end_at"]))
        self.assertEqual("scheduled", body["status"])

    def test_cancelling_keeps_the_record_and_marks_it_cancelled(self):
        created = self._create()

        response = self.client.post(f"/clinics/C1/appointments/{created['id']}/cancel")

        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual("cancelled", response.json()["status"])

        stored = self.client.get(f"/clinics/C1/appointments/{created['id']}")
        self.assertEqual(200, stored.status_code, stored.text)
        self.assertEqual("cancelled", stored.json()["status"])

    def test_cancelling_frees_the_professional_and_the_chair(self):
        created = self._create()
        cancelled = self.client.post(f"/clinics/C1/appointments/{created['id']}/cancel")
        self.assertEqual(200, cancelled.status_code, cancelled.text)

        reused = self._create()

        self.assertNotEqual(created["id"], reused["id"])
        self.assertEqual("scheduled", reused["status"])


class AppointmentApiErrorTests(AppointmentApiTestCase):
    """Mapeo explicito de errores y aislamiento entre consultorios."""

    def test_conflict_with_the_professional_returns_409_without_disclosing_the_patient(self):
        self._create(patient_id="patient-1")

        response = self.client.post(
            "/clinics/C1/appointments",
            json=self._payload(
                patient_id="patient-2",
                start_at=_local_time(9, 15).isoformat(),
                end_at=_local_time(9, 45).isoformat(),
            ),
        )

        self.assertEqual(409, response.status_code, response.text)
        body = response.json()
        self.assertEqual("appointment_conflict", body["code"])
        self.assertEqual("professional", body["resource"])
        self.assertNotIn("patient-1", response.text)
        self.assertNotIn("patient-2", response.text)

    def test_conflict_with_the_chair_of_another_professional_returns_409(self):
        self._create(professional_id="P1", chair_id="S1")

        response = self.client.post(
            "/clinics/C1/appointments",
            json=self._payload(
                professional_id="P2",
                chair_id="S1",
                start_at=_local_time(9, 15).isoformat(),
                end_at=_local_time(9, 45).isoformat(),
            ),
        )

        self.assertEqual(409, response.status_code, response.text)
        self.assertEqual("appointment_conflict", response.json()["code"])
        self.assertEqual("chair", response.json()["resource"])

    def test_rescheduling_into_a_conflict_keeps_the_original_interval(self):
        first = self._create()
        self._create(
            start_at=_local_time(11).isoformat(),
            end_at=_local_time(11, 30).isoformat(),
        )

        response = self.client.patch(
            f"/clinics/C1/appointments/{first['id']}",
            json={
                "start_at": _local_time(11).isoformat(),
                "end_at": _local_time(11, 30).isoformat(),
            },
        )

        self.assertEqual(409, response.status_code, response.text)
        stored = self.client.get(f"/clinics/C1/appointments/{first['id']}")
        self.assertEqual(_utc_time(12), datetime.fromisoformat(stored.json()["start_at"]))
        self.assertEqual(_utc_time(12, 30), datetime.fromisoformat(stored.json()["end_at"]))

    def test_empty_interval_returns_422_and_not_a_conflict(self):
        response = self.client.post(
            "/clinics/C1/appointments",
            json=self._payload(
                start_at=_local_time(9).isoformat(),
                end_at=_local_time(9).isoformat(),
            ),
        )

        self.assertEqual(422, response.status_code, response.text)
        body = response.json()
        self.assertEqual("invalid_appointment_interval", body["code"])
        self.assertNotIn("resource", body)

    def test_interval_without_timezone_returns_422(self):
        response = self.client.post(
            "/clinics/C1/appointments",
            json=self._payload(
                start_at="2026-10-15T09:00:00",
                end_at="2026-10-15T09:30:00",
            ),
        )

        self.assertEqual(422, response.status_code, response.text)
        self.assertEqual("invalid_appointment_interval", response.json()["code"])

    def test_unknown_professional_returns_422(self):
        response = self.client.post(
            "/clinics/C1/appointments",
            json=self._payload(professional_id="P9"),
        )

        self.assertEqual(422, response.status_code, response.text)
        self.assertEqual("resource_unavailable", response.json()["code"])

    def test_inactive_chair_returns_422(self):
        self._deactivate_chair("C1", "S1")

        response = self.client.post("/clinics/C1/appointments", json=self._payload())

        self.assertEqual(422, response.status_code, response.text)
        self.assertEqual("resource_unavailable", response.json()["code"])

    def test_unknown_appointment_returns_404(self):
        response = self.client.get("/clinics/C1/appointments/no-existe")

        self.assertEqual(404, response.status_code, response.text)
        self.assertEqual("appointment_not_found", response.json()["code"])

    def test_appointment_of_another_clinic_is_not_disclosed(self):
        created = self._create()

        response = self.client.get(f"/clinics/C2/appointments/{created['id']}")

        self.assertEqual(404, response.status_code, response.text)
        self.assertEqual("appointment_not_found", response.json()["code"])
        self.assertNotIn("patient-1", response.text)
        self.assertNotIn(created["id"], response.text)

    def test_chair_of_another_clinic_is_rejected(self):
        response = self.client.post(
            "/clinics/C2/appointments",
            json=self._payload(chair_id="S3"),
        )

        self.assertEqual(422, response.status_code, response.text)
        self.assertEqual("resource_unavailable", response.json()["code"])

    def test_same_resource_ids_in_another_clinic_do_not_conflict(self):
        self._create()

        response = self.client.post(
            "/clinics/C2/appointments",
            json=self._payload(),
        )

        self.assertEqual(201, response.status_code, response.text)
        self.assertEqual("C2", response.json()["clinic_id"])

    def test_chair_is_required_when_the_clinic_manages_chairs(self):
        response = self.client.post(
            "/clinics/C1/appointments",
            json=self._payload(chair_id=None),
        )

        self.assertEqual(422, response.status_code, response.text)
        self.assertEqual("chair_required", response.json()["code"])

    def test_unknown_request_field_returns_422(self):
        payload = self._payload()
        payload["datos_del_paciente"] = "no permitido"

        response = self.client.post("/clinics/C1/appointments", json=payload)

        self.assertEqual(422, response.status_code, response.text)
        self.assertEqual("invalid_request", response.json()["code"])

    def test_cancelling_an_unknown_appointment_returns_404(self):
        response = self.client.post("/clinics/C1/appointments/no-existe/cancel")

        self.assertEqual(404, response.status_code, response.text)
        self.assertEqual("appointment_not_found", response.json()["code"])


if __name__ == "__main__":
    unittest.main()
