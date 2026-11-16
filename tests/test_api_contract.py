"""Contrato HTTP de la API de turnos: mapeo de errores y esquemas.

Cada test de este archivo cubre un requisito de
``openspec/changes/c10-api-turnos-swagger/specs/appointment-api/spec.md``.
"""

import json
import unittest
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError

from src.api.errors import error_body, map_domain_error
from src.api.schemas import (
    AppointmentCreate,
    AppointmentResponse,
    RescheduleRequest,
)
from src.appointments import (
    Appointment,
    AppointmentConflict,
    AppointmentNotFound,
    ChairRequired,
    InvalidAppointmentInterval,
    ResourceUnavailable,
)


def _time(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 10, 15, hour, minute, tzinfo=timezone(timedelta(hours=-3)))


class DomainErrorMappingTests(unittest.TestCase):
    """Los errores del dominio se traducen a codigos HTTP distintos y predecibles."""

    def test_conflict_maps_to_409_and_keeps_the_conflicting_resource(self):
        mapping = map_domain_error(AppointmentConflict("professional"))

        self.assertEqual(409, mapping.status_code)
        self.assertEqual("appointment_conflict", mapping.code)
        self.assertEqual("professional", mapping.resource)

    def test_chair_conflict_keeps_the_chair_as_the_conflicting_resource(self):
        mapping = map_domain_error(AppointmentConflict("chair"))

        self.assertEqual(409, mapping.status_code)
        self.assertEqual("appointment_conflict", mapping.code)
        self.assertEqual("chair", mapping.resource)

    def test_invalid_interval_maps_to_422(self):
        mapping = map_domain_error(InvalidAppointmentInterval("start_at must be before end_at"))

        self.assertEqual(422, mapping.status_code)
        self.assertEqual("invalid_appointment_interval", mapping.code)

    def test_resource_unavailable_maps_to_422(self):
        mapping = map_domain_error(ResourceUnavailable("Resource is unavailable"))

        self.assertEqual(422, mapping.status_code)
        self.assertEqual("resource_unavailable", mapping.code)

    def test_chair_required_maps_to_422(self):
        mapping = map_domain_error(ChairRequired("A chair must be selected"))

        self.assertEqual(422, mapping.status_code)
        self.assertEqual("chair_required", mapping.code)

    def test_appointment_not_found_maps_to_404(self):
        mapping = map_domain_error(AppointmentNotFound("Appointment not found"))

        self.assertEqual(404, mapping.status_code)
        self.assertEqual("appointment_not_found", mapping.code)

    def test_every_domain_error_maps_to_a_distinct_status(self):
        mappings = [
            map_domain_error(AppointmentConflict("professional")),
            map_domain_error(InvalidAppointmentInterval("invalid")),
            map_domain_error(ChairRequired("chair")),
            map_domain_error(ResourceUnavailable("resource")),
            map_domain_error(AppointmentNotFound("missing")),
        ]

        # 409 conflicto, 422 validacion o recurso no disponible, 404 no encontrado.
        self.assertEqual({409, 422, 404}, {mapping.status_code for mapping in mappings})
        self.assertEqual(5, len({mapping.code for mapping in mappings}))


class ErrorBodyTests(unittest.TestCase):
    """El cuerpo del error es controlado y no filtra identidad del paciente."""

    def test_body_exposes_only_the_documented_keys(self):
        body = error_body(map_domain_error(AppointmentConflict("professional")))

        self.assertEqual({"code", "detail", "resource"}, set(body))
        self.assertEqual("appointment_conflict", body["code"])
        self.assertEqual("professional", body["resource"])
        self.assertTrue(body["detail"])

    def test_body_without_a_conflicting_resource_omits_the_resource_key(self):
        body = error_body(map_domain_error(AppointmentNotFound("missing")))

        self.assertEqual({"code", "detail"}, set(body))
        self.assertNotIn("patient", body["code"])

    def test_body_never_echoes_the_underlying_exception_text(self):
        class LeakyConflict(AppointmentConflict):
            def __init__(self) -> None:
                super().__init__("professional")
                self.args = ("appointment_conflict:professional:patient-9-datos-secretos",)

        body = error_body(map_domain_error(LeakyConflict()))
        rendered = json.dumps(body, ensure_ascii=False)

        self.assertNotIn("patient-9-datos-secretos", rendered)
        self.assertNotIn("patient", rendered)


class SchemaTests(unittest.TestCase):
    """Los esquemas de request y response reflejan el contrato del dominio."""

    def test_create_schema_requires_the_operational_fields(self):
        body = AppointmentCreate(
            professional_id="P1",
            patient_id="PT1",
            service_id="SV1",
            start_at=_time(9),
            end_at=_time(9, 30),
        )

        self.assertEqual("P1", body.professional_id)
        self.assertEqual("PT1", body.patient_id)
        self.assertEqual("SV1", body.service_id)
        self.assertIsNone(body.chair_id)

    def test_create_schema_rejects_unknown_fields(self):
        with self.assertRaises(ValidationError):
            AppointmentCreate(
                professional_id="P1",
                patient_id="PT1",
                service_id="SV1",
                start_at=_time(9),
                end_at=_time(9, 30),
                datos_del_paciente="no permitido",
            )

    def test_reschedule_schema_carries_only_the_interval(self):
        body = RescheduleRequest(start_at=_time(11), end_at=_time(11, 30))

        self.assertEqual(_time(11), body.start_at)
        self.assertEqual(_time(11, 30), body.end_at)
        self.assertEqual({"start_at", "end_at"}, set(RescheduleRequest.model_fields))

    def test_response_schema_is_built_from_the_domain_appointment(self):
        appointment = Appointment(
            id="AP1",
            clinic_id="C1",
            professional_id="P1",
            chair_id="S1",
            patient_id="PT1",
            service_id="SV1",
            start_at=_time(9),
            end_at=_time(9, 30),
            status="scheduled",
        )

        response = AppointmentResponse.model_validate(appointment)

        self.assertEqual("AP1", response.id)
        self.assertEqual("C1", response.clinic_id)
        self.assertEqual("P1", response.professional_id)
        self.assertEqual("S1", response.chair_id)
        self.assertEqual("PT1", response.patient_id)
        self.assertEqual("SV1", response.service_id)
        self.assertEqual("scheduled", response.status)
        self.assertEqual(_time(9), response.start_at)
        self.assertEqual(_time(9, 30), response.end_at)

    def test_response_schema_keeps_a_missing_chair_as_none(self):
        appointment = Appointment(
            id="AP1",
            clinic_id="C1",
            professional_id="P1",
            chair_id=None,
            patient_id="PT1",
            service_id="SV1",
            start_at=_time(9),
            end_at=_time(9, 30),
            status="scheduled",
        )

        response = AppointmentResponse.model_validate(appointment)

        self.assertIsNone(response.chair_id)


if __name__ == "__main__":
    unittest.main()
