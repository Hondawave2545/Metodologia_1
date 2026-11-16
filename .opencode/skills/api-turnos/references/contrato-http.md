# Contrato HTTP de la API de turnos

Referencia rápida de la capa HTTP. **La fuente normativa es la spec vigente**:
`openspec/specs/appointment-api/spec.md`. Si este documento y la spec discrepan, la spec gana.

- App: `src/api/main.py` (`create_app()` y `app = create_app()`).
- Esquemas: `src/api/schemas.py`. Mapeo de errores: `src/api/errors.py`.
- Dominio: `src/appointments.py`.
- Swagger en `/docs`, contrato en `/openapi.json` (OpenAPI `3.1.0`).

Metadatos: `title="Turnos Odontologia API"`, `version="0.1.0"`.

---

## 1. Rutas

| Método | Ruta | Éxito | Request | Response |
|---|---|---|---|---|
| `POST` | `/clinics/{clinic_id}/appointments` | `201 Created` | `AppointmentCreate` | `AppointmentResponse` |
| `GET` | `/clinics/{clinic_id}/appointments/{appointment_id}` | `200 OK` | — (path params) | `AppointmentResponse` |
| `PATCH` | `/clinics/{clinic_id}/appointments/{appointment_id}` | `200 OK` | `RescheduleRequest` | `AppointmentResponse` |
| `POST` | `/clinics/{clinic_id}/appointments/{appointment_id}/cancel` | `200 OK` | — | `AppointmentResponse` (ya cancelado) |
| `GET` | `/clinics/{clinic_id}/availability` | `200 OK` | — (query params) | `AvailabilityResponse` |

No existe listado: `GET /clinics/{clinic_id}/appointments` devuelve `405`. La cancelación **no** es `204`
ni `DELETE`: devuelve `200` con el turno ya cancelado. La consulta de disponibilidad no es un listado: no
devuelve turnos, sino si la franja está libre y qué recurso la ocupa.

---

## 2. Esquemas

### `AppointmentCreate` (cuerpo de `POST`)

`model_config = ConfigDict(extra="forbid")`

| Campo | Tipo | Obligatorio |
|---|---|---|
| `professional_id` | `str` | sí |
| `patient_id` | `str` | sí |
| `service_id` | `str` | sí |
| `start_at` | `datetime` (`format: date-time`) | sí |
| `end_at` | `datetime` (`format: date-time`) | sí |
| `chair_id` | `str \| None` | no |

`required`: `["professional_id", "patient_id", "service_id", "start_at", "end_at"]` · `additionalProperties: false`.

### `RescheduleRequest` (cuerpo de `PATCH`)

`model_config = ConfigDict(extra="forbid")`

| Campo | Tipo | Obligatorio |
|---|---|---|
| `start_at` | `datetime` (`format: date-time`) | sí |
| `end_at` | `datetime` (`format: date-time`) | sí |

`required`: `["start_at", "end_at"]` · `additionalProperties: false`. La operación cambia **solo** el
intervalo: por eso es `PATCH` y no `PUT`.

### `AppointmentResponse` (cuerpo de todas las respuestas exitosas)

`model_config = ConfigDict(from_attributes=True)`

| Campo | Tipo |
|---|---|
| `id` | `str` (UUID v4) |
| `clinic_id` | `str` |
| `professional_id` | `str` |
| `chair_id` | `str \| None` |
| `patient_id` | `str` |
| `service_id` | `str` |
| `start_at` | `datetime` (`format: date-time`) |
| `end_at` | `datetime` (`format: date-time`) |
| `status` | `str` |

`response_model` **filtra** la respuesta: solo salen estos 9 campos.

---

## 3. Mapeo de errores del dominio

Literal de `src/api/errors.py` (`DETAILS`):

```python
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
```

Literal de `_MAPPINGS`:

```python
_MAPPINGS: tuple[tuple[type[AppointmentError], int, str], ...] = (
    (AppointmentConflict, 409, "appointment_conflict"),
    (InvalidAppointmentInterval, 422, "invalid_appointment_interval"),
    (ChairRequired, 422, "chair_required"),
    (ResourceUnavailable, 422, "resource_unavailable"),
    (AppointmentNotFound, 404, "appointment_not_found"),
)
```

| Excepción de dominio | HTTP | `code` | Disparador |
|---|---|---|---|
| `AppointmentConflict` | `409` | `appointment_conflict` | solapamiento de profesional o de sillón |
| `InvalidAppointmentInterval` | `422` | `invalid_appointment_interval` | intervalo sin zona horaria, o `start_at >= end_at` |
| `ChairRequired` | `422` | `chair_required` | el consultorio administra sillones y el body no trae `chair_id` |
| `ResourceUnavailable` | `422` | `resource_unavailable` | consultorio, profesional, paciente, servicio o sillón inexistente/inactivo, o de otro consultorio; también turno no activo al reprogramar |
| `AppointmentNotFound` | `404` | `appointment_not_found` | el turno no existe en el consultorio, o ya no está activo al cancelar |
| `RequestValidationError` | `422` | `invalid_request` | campo extra, campo faltante, JSON malformado, tipo inválido |

### Forma del cuerpo

```json
{"code": "...", "detail": "...", "resource": "..."}
```

`resource` aparece **solo** en `appointment_conflict`, con valor `"professional"` o `"chair"`. Cuando no
hay recurso, la clave **no existe** (no es `null`).

```json
{"code":"appointment_conflict","detail":"El recurso indicado ya está ocupado en ese intervalo.","resource":"professional"}
{"code":"resource_unavailable","detail":"El recurso indicado no existe, está inactivo o pertenece a otro consultorio."}
```

El `detail` sale **siempre** de `DETAILS`, nunca del mensaje de la excepción: por eso el cuerpo de error
no puede filtrar datos del paciente. Si alguna vez aparece texto libre, es un bug.

### Errores que no son del dominio

| Situación | Respuesta |
|---|---|
| ruta inexistente | `404 {"detail":"Not Found"}` |
| método incorrecto (p. ej. `GET` en la colección, `DELETE`) | `405 {"detail":"Method Not Allowed"}` |

---

## 4. Consulta de disponibilidad

`GET /clinics/{clinic_id}/availability` es de **solo lectura**: no crea ni modifica turnos.

| Parámetro | Obligatorio | Tipo |
|---|---|---|
| `start_at` | sí | `datetime` con zona horaria |
| `end_at` | sí | `datetime` con zona horaria |
| `professional_id` | sí | `str` |
| `chair_id` | no (obligatorio si el consultorio administra sillones) | `str` |

Respuesta `200` (`AvailabilityResponse`):

```json
{
  "clinic_id": "demo-clinic",
  "professional_id": "demo-profesional",
  "chair_id": "demo-sillon",
  "start_at": "2026-12-01T12:00:00Z",
  "end_at": "2026-12-01T12:30:00Z",
  "available": true,
  "conflicting_resource": null
}
```

- `conflicting_resource` es `"professional"` o `"chair"` cuando `available` es `false`, y `null` cuando está
  libre. El cuerpo **no** incluye turnos ni datos de paciente.
- Un conflicto **no** es un error: la respuesta es `200`. Los `409` son exclusivos del alta y la reprogramación.
- Errores: `422 invalid_appointment_interval` (intervalo inválido o sin zona horaria), `422
  resource_unavailable` (consultorio, profesional o sillón inexistente/inactivo/ajeno) y `422 chair_required`
  (consultorio que administra sillones y la consulta no indica sillón).
- El razonamiento del dominio es el mismo del alta: intervalos semiabiertos `[inicio, fin)` y solo
  `scheduled` y `confirmed` bloquean. Un turno cancelado no bloquea.
- La consulta es orientativa: entre el `GET` y el alta otro turno puede ocupar la franja. El alta sigue
  validando y sigue respondiendo `409`.

---

## 5. Semántica de intervalos y estados

- Los turnos son intervalos **semiabiertos `[inicio, fin)`**: dos turnos consecutivos que se tocan
  **no** chocan. La consulta de conflicto usa `start_at < <fin nuevo> AND end_at > <inicio nuevo>`.
- Estados que **bloquean** profesional y sillón: `scheduled` y `confirmed`.
  (`ACTIVE_STATUSES = ("scheduled", "confirmed")`.)
- Estado inicial al crear: `scheduled`.
- Cancelar: pasa a `cancelled` y libera profesional y sillón (conserva el registro).
- `start_at` y `end_at` **exigen zona horaria**: sin `tzinfo` la API responde
  `422 invalid_appointment_interval`.
- La API **siempre devuelve UTC** (`Z`); un request con `-03:00` se normaliza a UTC.

---

## 6. Datos de demostración

```bash
.venv\Scripts\python.exe scripts\seed_demo_data.py
.venv\Scripts\python.exe scripts\seed_demo_data.py --database data/otra-base.sqlite3
```

| Recurso | Identificador |
|---|---|
| Consultorio | `demo-clinic` |
| Profesional | `demo-profesional` |
| Sillón | `demo-sillon` |
| Paciente | `demo-paciente` |
| Servicio | `demo-consulta` |

El consultorio demo se crea con `manages_chairs=True`: para crear turnos con estos identificadores hay
que mandar **`chair_id: "demo-sillon"`**, o la API responde `422 chair_required`. Lo mismo vale para la
consulta de disponibilidad.

El script es **idempotente**: no borra ni sobrescribe registros preexistentes.

---

## 7. Ejemplos

Crear (con `chair_id`):

```bash
curl -X POST http://127.0.0.1:8000/clinics/demo-clinic/appointments \
  -H "Content-Type: application/json" \
  -d '{"professional_id":"demo-profesional","patient_id":"demo-paciente","service_id":"demo-consulta","chair_id":"demo-sillon","start_at":"2026-11-16T09:00:00-03:00","end_at":"2026-11-16T10:00:00-03:00"}'
```

Consultar:

```bash
curl http://127.0.0.1:8000/clinics/demo-clinic/appointments/<id>
```

Reprogramar:

```bash
curl -X PATCH http://127.0.0.1:8000/clinics/demo-clinic/appointments/<id> \
  -H "Content-Type: application/json" \
  -d '{"start_at":"2026-11-16T11:00:00-03:00","end_at":"2026-11-16T12:00:00-03:00"}'
```

Cancelar:

```bash
curl -X POST http://127.0.0.1:8000/clinics/demo-clinic/appointments/<id>/cancel
```

Consultar la disponibilidad:

```bash
curl "http://127.0.0.1:8000/clinics/demo-clinic/availability?start_at=2026-11-16T09:00:00-03:00&end_at=2026-11-16T10:00:00-03:00&professional_id=demo-profesional&chair_id=demo-sillon"
```

---

## 8. Fuera de alcance

No hay autenticación, no hay listados y no hay alta de recursos (consultorios, profesionales, sillones,
pacientes, servicios). No están en el alcance de C-10 ni de C-11 y no deben aparecer por conveniencia.
