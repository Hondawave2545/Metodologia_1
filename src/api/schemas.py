"""Esquemas de request y response de la API de turnos.

El intervalo se modela como ``datetime`` con zona horaria explicita. La
validacion del intervalo (inicio anterior al fin, zona horaria presente) la
resuelve el dominio, de modo que la API lo traduzca al mismo codigo de error
que el resto de los errores de dominio.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppointmentCreate(BaseModel):
    """Datos de entrada para crear un turno."""

    model_config = ConfigDict(extra="forbid")

    professional_id: str
    patient_id: str
    service_id: str
    start_at: datetime
    end_at: datetime
    chair_id: str | None = None


class RescheduleRequest(BaseModel):
    """Datos de entrada para reprogramar un turno: solo su intervalo."""

    model_config = ConfigDict(extra="forbid")

    start_at: datetime
    end_at: datetime


class AppointmentResponse(BaseModel):
    """Datos operativos de un turno, tal como los expone el dominio."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    clinic_id: str
    professional_id: str
    chair_id: str | None
    patient_id: str
    service_id: str
    start_at: datetime
    end_at: datetime
    status: str


class ErrorResponse(BaseModel):
    """Cuerpo de error de la API, con codigo estable y texto controlado."""

    code: str
    detail: str
    resource: str | None = None


class AvailabilityResponse(BaseModel):
    """Resultado de consultar la disponibilidad de un intervalo.

    No incluye ningun turno ni dato de paciente: solo si el intervalo esta
    libre y que tipo de recurso lo ocupa.
    """

    clinic_id: str
    professional_id: str
    chair_id: str | None
    start_at: datetime
    end_at: datetime
    available: bool
    conflicting_resource: str | None = None
