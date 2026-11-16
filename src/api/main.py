"""Aplicacion HTTP de la API de turnos.

Es un adaptador delgado sobre ``src/appointments.py``: traduce requests a
llamadas del dominio y errores del dominio a respuestas HTTP. La regla de
negocio (solapamientos, estados que bloquean, aislamiento por consultorio) no
se reimplementa aqui.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.dependencies import get_repository
from src.api.errors import DETAILS, error_body, map_domain_error
from src.api.schemas import (
    AppointmentCreate,
    AppointmentResponse,
    AvailabilityResponse,
    ErrorResponse,
    RescheduleRequest,
)
from src.appointments import AppointmentError, AppointmentRepository

Repository = Annotated[AppointmentRepository, Depends(get_repository)]

_CONFLICT_RESPONSE = {409: {"model": ErrorResponse, "description": "Recurso en conflicto"}}
_VALIDATION_RESPONSE = {422: {"model": ErrorResponse, "description": "Datos invalidos"}}
_NOT_FOUND_RESPONSE = {404: {"model": ErrorResponse, "description": "Turno no encontrado"}}


def create_app() -> FastAPI:
    """Construye la aplicacion de la API de turnos."""

    app = FastAPI(
        title="Turnos Odontologia API",
        version="0.1.0",
        summary="API local de turnos para demostrar el prototipo de agenda.",
        description=(
            "Expone crear, consultar, reprogramar y cancelar turnos sobre el "
            "servicio de dominio ya implementado. Sin autenticacion, sin datos "
            "reales y solo para loopback local."
        ),
    )

    @app.exception_handler(AppointmentError)
    async def handle_domain_error(
        request: Request, exc: AppointmentError
    ) -> JSONResponse:
        mapping = map_domain_error(exc)
        return JSONResponse(
            status_code=mapping.status_code, content=error_body(mapping)
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"code": "invalid_request", "detail": DETAILS["invalid_request"]},
        )

    @app.post(
        "/clinics/{clinic_id}/appointments",
        status_code=status.HTTP_201_CREATED,
        response_model=AppointmentResponse,
        responses={**_CONFLICT_RESPONSE, **_VALIDATION_RESPONSE},
        summary="Crear un turno",
    )
    def create_appointment(
        clinic_id: str, body: AppointmentCreate, repository: Repository
    ) -> AppointmentResponse:
        appointment = repository.create_appointment(
            clinic_id=clinic_id,
            professional_id=body.professional_id,
            patient_id=body.patient_id,
            service_id=body.service_id,
            start_at=body.start_at,
            end_at=body.end_at,
            chair_id=body.chair_id,
        )
        return AppointmentResponse.model_validate(appointment)

    @app.get(
        "/clinics/{clinic_id}/appointments/{appointment_id}",
        response_model=AppointmentResponse,
        responses={**_NOT_FOUND_RESPONSE},
        summary="Consultar un turno",
    )
    def get_appointment(
        clinic_id: str, appointment_id: str, repository: Repository
    ) -> AppointmentResponse:
        appointment = repository.get_appointment(
            clinic_id=clinic_id, appointment_id=appointment_id
        )
        return AppointmentResponse.model_validate(appointment)

    @app.patch(
        "/clinics/{clinic_id}/appointments/{appointment_id}",
        response_model=AppointmentResponse,
        responses={
            **_CONFLICT_RESPONSE,
            **_VALIDATION_RESPONSE,
            **_NOT_FOUND_RESPONSE,
        },
        summary="Reprogramar un turno",
    )
    def reschedule_appointment(
        clinic_id: str,
        appointment_id: str,
        body: RescheduleRequest,
        repository: Repository,
    ) -> AppointmentResponse:
        appointment = repository.reschedule_appointment(
            clinic_id=clinic_id,
            appointment_id=appointment_id,
            start_at=body.start_at,
            end_at=body.end_at,
        )
        return AppointmentResponse.model_validate(appointment)

    @app.post(
        "/clinics/{clinic_id}/appointments/{appointment_id}/cancel",
        response_model=AppointmentResponse,
        responses={**_NOT_FOUND_RESPONSE, **_VALIDATION_RESPONSE},
        summary="Cancelar un turno",
    )
    def cancel_appointment(
        clinic_id: str, appointment_id: str, repository: Repository
    ) -> AppointmentResponse:
        repository.cancel_appointment(
            clinic_id=clinic_id, appointment_id=appointment_id
        )
        appointment = repository.get_appointment(
            clinic_id=clinic_id, appointment_id=appointment_id
        )
        return AppointmentResponse.model_validate(appointment)

    @app.get(
        "/clinics/{clinic_id}/availability",
        response_model=AvailabilityResponse,
        responses={**_VALIDATION_RESPONSE},
        summary="Consultar la disponibilidad de un intervalo",
    )
    def check_availability(
        clinic_id: str,
        repository: Repository,
        start_at: Annotated[
            datetime,
            Query(description="Inicio del intervalo, con zona horaria explicita."),
        ],
        end_at: Annotated[
            datetime,
            Query(description="Fin del intervalo, con zona horaria explicita."),
        ],
        professional_id: Annotated[
            str, Query(description="Profesional que se quiere reservar.")
        ],
        chair_id: Annotated[
            str | None,
            Query(description="Sillon que se quiere reservar."),
        ] = None,
    ) -> AvailabilityResponse:
        conflicting_resource = repository.check_availability(
            clinic_id=clinic_id,
            professional_id=professional_id,
            chair_id=chair_id,
            start_at=start_at,
            end_at=end_at,
        )
        # El dominio ya rechazo los intervalos sin zona horaria, asi que
        # normalizar a UTC es seguro aca.
        return AvailabilityResponse(
            clinic_id=clinic_id,
            professional_id=professional_id,
            chair_id=chair_id,
            start_at=start_at.astimezone(timezone.utc),
            end_at=end_at.astimezone(timezone.utc),
            available=conflicting_resource is None,
            conflicting_resource=conflicting_resource,
        )

    return app


app = create_app()
