"""Traduccion explicita de los errores del dominio de turnos a respuestas HTTP.

El cuerpo del error se construye con textos controlados: nunca se reenvia el
mensaje de la excepcion del dominio, para que ningun dato del paciente pueda
filtrar en la respuesta.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.appointments import (
    AppointmentConflict,
    AppointmentError,
    AppointmentNotFound,
    ChairRequired,
    InvalidAppointmentInterval,
    ResourceUnavailable,
)


@dataclass(frozen=True)
class ErrorMapping:
    """Codigo HTTP, codigo estable y recurso en conflicto de un error del dominio."""

    status_code: int
    code: str
    resource: str | None = None


DETAILS: dict[str, str] = {
    "appointment_conflict": "El recurso indicado ya está ocupado en ese intervalo.",
    "invalid_appointment_interval": "El intervalo indicado no es válido.",
    "chair_required": "El consultorio administra sillones y el turno debe indicar uno.",
    "resource_unavailable": (
        "El recurso indicado no existe, está inactivo o pertenece a otro consultorio."
    ),
    "appointment_not_found": "El turno no existe en el consultorio indicado.",
    "invalid_request": "La solicitud no cumple el contrato de la API.",
}


_MAPPINGS: tuple[tuple[type[AppointmentError], int, str], ...] = (
    (AppointmentConflict, 409, "appointment_conflict"),
    (InvalidAppointmentInterval, 422, "invalid_appointment_interval"),
    (ChairRequired, 422, "chair_required"),
    (ResourceUnavailable, 422, "resource_unavailable"),
    (AppointmentNotFound, 404, "appointment_not_found"),
)


def map_domain_error(error: AppointmentError) -> ErrorMapping:
    """Traduce un error del dominio al codigo HTTP y al codigo estable de la API."""

    for error_type, status_code, code in _MAPPINGS:
        if isinstance(error, error_type):
            resource = getattr(error, "resource", None)
            return ErrorMapping(
                status_code=status_code,
                code=code,
                resource=resource if isinstance(resource, str) else None,
            )
    raise error


def error_body(mapping: ErrorMapping) -> dict[str, str]:
    """Construye el cuerpo de la respuesta de error con textos controlados."""

    body = {"code": mapping.code, "detail": DETAILS[mapping.code]}
    if mapping.resource is not None:
        body["resource"] = mapping.resource
    return body
