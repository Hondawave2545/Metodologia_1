# Evidencia: verificacion real por HTTP de la API de turnos

Verificacion ejecutada contra **uvicorn levantado como proceso real**, no contra el
cliente de pruebas. Cada bloque registra la solicitud enviada y la respuesta recibida.

- Fecha de la verificacion: 2026-11-14 (original) y 2026-11-16 (reverificacion, seccion 0)
- Servidor: `python -m uvicorn src.api.main:app --host 127.0.0.1 --port <puerto libre>`
- Base de datos: `data/demo.sqlite3`, preparada con `scripts/seed_demo_data.py`
- Los turnos usan la fecha futura 2026-12-01 para no chocar con datos previos.

---

## 0. Reverificacion del 2026-11-16

La secuencia completa de mas abajo se **reejecuto** el 2026-11-16, desde cero, para comprobar que la
evidencia no era una transcripcion sino un resultado reproducible.

| Aspecto | Detalle |
|---|---|
| Base de datos | `data/verificacion-http.sqlite3` (base nueva, sembrada con `scripts/seed_demo_data.py`; la base `data/demo.sqlite3` no se toco) |
| Variable de entorno | `APPOINTMENTS_DB_PATH=data/verificacion-http.sqlite3` |
| Comando de arranque | `.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 56591` (puerto libre elegido por el script) |
| Cliente HTTP | `curl.exe` sobre TCP contra `127.0.0.1` (no el cliente de pruebas del proyecto) |
| Identificador del turno | `d5006225-b4ef-438e-aea4-c49f79f96eda` |

| # | Operacion | Esperado | Obtenido (2026-11-16) | Cuerpo |
|---|---|---|---|---|
| 1 | `GET /docs` | 200 | **200** | HTML de Swagger UI |
| 2 | `GET /openapi.json` | 200 | **200** | OpenAPI `3.1.0` con las 4 operaciones |
| 3 | `POST .../appointments` | 201 | **201** | turno creado, `status: scheduled` |
| 4 | `GET .../appointments/{id}` | 200 | **200** | mismo intervalo y estado |
| 5 | `PATCH .../appointments/{id}` | 200 | **200** | intervalo nuevo `14:00:00Z` |
| 6 | `POST .../appointments` (conflicto) | 409 | **409** | `appointment_conflict`, `resource: professional` |
| 7 | `POST .../appointments` (intervalo invalido) | 422 | **422** | `invalid_appointment_interval` |
| 8 | `GET .../appointments/no-existe` | 404 | **404** | `appointment_not_found` |
| 9 | `POST .../appointments/{id}/cancel` | 200 | **200** | turno con `status: cancelled` |
| 10 | `GET .../appointments/{id}` (tras cancelar) | 200 | **200** | `status: cancelled` persistido |

Los 10 codigos coinciden con los del 2026-11-14 y los cuerpos tienen la misma forma. **La cancelacion
responde `200` con el turno cancelado en el cuerpo, nunca `204`.** El cuerpo del conflicto no contiene
ninguna identidad de paciente: solo el texto controlado y el recurso en conflicto.

> Una nota de método: en el primer intento de esta reverificacion los `POST` devolvieron `422
> invalid_request`. La causa no era la API sino PowerShell, que mutila las comillas dobles al pasar
> argumentos a un ejecutable nativo; el JSON llegaba malformado. Se resolvio pasando el cuerpo por
> archivo (`curl --data-binary @archivo`). Se deja registrado porque es la clase de error que hace
> creer que la API fallo cuando el problema es del cliente.

---

## 0.1. Consulta de disponibilidad (C-11) — verificada el 2026-11-16

Secuencia real por HTTP de la quinta operación, `GET /clinics/{clinic_id}/availability`, contra uvicorn
levantado como proceso real.

| Aspecto | Detalle |
|---|---|
| Base de datos | `data/verificacion-disponibilidad.sqlite3` (base nueva, sembrada con `scripts/seed_demo_data.py`) |
| Comando de arranque | `.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 56966` |
| Cliente HTTP | `curl.exe` sobre TCP contra `127.0.0.1` |
| Extra | Un segundo profesional ficticio, `demo-profesional-2`, registrado con la API pública del repositorio (el demo trae uno solo y sin él el conflicto de sillón no se puede provocar por HTTP) |

### 1. Intervalo libre

```http
GET /clinics/demo-clinic/availability?start_at=2026-12-01T09:00:00-03:00&end_at=2026-12-01T09:30:00-03:00&professional_id=demo-profesional&chair_id=demo-sillon
```

```http
HTTP 200
```

```json
{"clinic_id":"demo-clinic","professional_id":"demo-profesional","chair_id":"demo-sillon","start_at":"2026-12-01T12:00:00Z","end_at":"2026-12-01T12:30:00Z","available":true,"conflicting_resource":null}
```

### 2. Se crea el turno que ocupa la franja

```http
POST /clinics/demo-clinic/appointments
Content-Type: application/json

{"professional_id":"demo-profesional","patient_id":"demo-paciente","service_id":"demo-consulta","chair_id":"demo-sillon","start_at":"2026-12-01T09:00:00-03:00","end_at":"2026-12-01T09:30:00-03:00"}
```

```http
HTTP 201
```

```json
{"id":"d05852ab-bc96-46e1-acfa-df434ce8ff95","clinic_id":"demo-clinic","professional_id":"demo-profesional","chair_id":"demo-sillon","patient_id":"demo-paciente","service_id":"demo-consulta","start_at":"2026-12-01T12:00:00Z","end_at":"2026-12-01T12:30:00Z","status":"scheduled"}
```

### 3. La misma franja, con el profesional ocupado

```http
GET /clinics/demo-clinic/availability?start_at=2026-12-01T09:00:00-03:00&end_at=2026-12-01T09:30:00-03:00&professional_id=demo-profesional&chair_id=demo-sillon
```

```http
HTTP 200
```

```json
{"clinic_id":"demo-clinic","professional_id":"demo-profesional","chair_id":"demo-sillon","start_at":"2026-12-01T12:00:00Z","end_at":"2026-12-01T12:30:00Z","available":false,"conflicting_resource":"professional"}
```

Un conflicto es el **resultado** de la consulta, no un error: el código es `200`, no `409`.

### 4. Otro profesional, mismo sillón: el sillón es el recurso en conflicto

```http
GET /clinics/demo-clinic/availability?start_at=2026-12-01T09:00:00-03:00&end_at=2026-12-01T09:30:00-03:00&professional_id=demo-profesional-2&chair_id=demo-sillon
```

```http
HTTP 200
```

```json
{"clinic_id":"demo-clinic","professional_id":"demo-profesional-2","chair_id":"demo-sillon","start_at":"2026-12-01T12:00:00Z","end_at":"2026-12-01T12:30:00Z","available":false,"conflicting_resource":"chair"}
```

Ninguna de estas respuestas contiene el identificador del turno en conflicto ni dato de paciente.

### 5. Intervalo inválido

```http
GET /clinics/demo-clinic/availability?start_at=2026-12-01T10:00:00-03:00&end_at=2026-12-01T09:00:00-03:00&professional_id=demo-profesional&chair_id=demo-sillon
```

```http
HTTP 422
```

```json
{"code":"invalid_appointment_interval","detail":"El intervalo indicado no es válido."}
```

### 6. Sin sillón, en un consultorio que administra sillones

```http
GET /clinics/demo-clinic/availability?start_at=2026-12-01T11:00:00-03:00&end_at=2026-12-01T11:30:00-03:00&professional_id=demo-profesional
```

```http
HTTP 422
```

```json
{"code":"chair_required","detail":"El consultorio administra sillones y el turno debe indicar uno."}
```

### 7. Profesional inexistente

```http
GET /clinics/demo-clinic/availability?start_at=2026-12-01T11:00:00-03:00&end_at=2026-12-01T11:30:00-03:00&professional_id=profesional-inexistente&chair_id=demo-sillon
```

```http
HTTP 422
```

```json
{"code":"resource_unavailable","detail":"El recurso indicado no existe, está inactivo o pertenece a otro consultorio."}
```

### 8. Parámetro obligatorio ausente

```http
GET /clinics/demo-clinic/availability?start_at=2026-12-01T11:00:00-03:00&end_at=2026-12-01T11:30:00-03:00
```

```http
HTTP 422
```

```json
{"code":"invalid_request","detail":"La solicitud no cumple el contrato de la API."}
```

### 9. Cancelar y volver a consultar

```http
POST /clinics/demo-clinic/appointments/d05852ab-bc96-46e1-acfa-df434ce8ff95/cancel
```

```http
HTTP 200
```

```json
{"id":"d05852ab-bc96-46e1-acfa-df434ce8ff95","clinic_id":"demo-clinic","professional_id":"demo-profesional","chair_id":"demo-sillon","patient_id":"demo-paciente","service_id":"demo-consulta","start_at":"2026-12-01T12:00:00Z","end_at":"2026-12-01T12:30:00Z","status":"cancelled"}
```

```http
GET /clinics/demo-clinic/availability?start_at=2026-12-01T09:00:00-03:00&end_at=2026-12-01T09:30:00-03:00&professional_id=demo-profesional&chair_id=demo-sillon
```

```http
HTTP 200
```

```json
{"clinic_id":"demo-clinic","professional_id":"demo-profesional","chair_id":"demo-sillon","start_at":"2026-12-01T12:00:00Z","end_at":"2026-12-01T12:30:00Z","available":true,"conflicting_resource":null}
```

Un turno cancelado libera el profesional y el sillón: la franja vuelve a estar disponible.

### Resumen de la secuencia de disponibilidad

| # | Caso | Esperado | Obtenido |
|---|---|---|---|
| 1 | intervalo libre | 200, `available: true` | **200**, `available: true` |
| 2 | crear el turno | 201 | **201** |
| 3 | profesional ocupado | 200, `professional` | **200**, `professional` |
| 4 | sillón ocupado | 200, `chair` | **200**, `chair` |
| 5 | intervalo inválido | 422 | **422** `invalid_appointment_interval` |
| 6 | sin sillón | 422 | **422** `chair_required` |
| 7 | profesional inexistente | 422 | **422** `resource_unavailable` |
| 8 | parámetro obligatorio ausente | 422 | **422** `invalid_request` |
| 9 | cancelar | 200 | **200** |
| 10 | tras cancelar | 200, `available: true` | **200**, `available: true` |

---

## Datos de demostracion usados

```
consultorio : demo-clinic
profesional : demo-profesional
sillon      : demo-sillon
paciente    : demo-paciente
servicio    : demo-consulta
```

## Resumen

| # | Operacion | Resultado esperado | Resultado obtenido |
|---|---|---|---|
| 1 | `GET /docs` | 200 | **200** |
| 2 | `GET /openapi.json` | 200 | **200** |
| 3 | `POST .../appointments` | 201 | **201** |
| 4 | `GET .../appointments/{id}` | 200 | **200** |
| 5 | `PATCH .../appointments/{id}` | 200 | **200** |
| 6 | `POST .../appointments (conflicto)` | 409 | **409** |
| 7 | `POST .../appointments (intervalo invalido)` | 422 | **422** |
| 8 | `GET .../appointments/no-existe` | 404 | **404** |
| 9 | `POST .../appointments/{id}/cancel` | 200 | **200** |
| 10 | `GET .../appointments/{id} (tras cancelar)` | 200 | **200** |

## Solicitudes y respuestas

### 1. Documentacion interactiva de Swagger

**Solicitud**

```http
GET /docs
```

**Respuesta**

```http
HTTP 200
Content-Type: text/html; charset=utf-8
```

```

    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
... (documento HTML completo)
```

### 2. Esquema OpenAPI de la API

**Solicitud**

```http
GET /openapi.json
```

**Respuesta**

```http
HTTP 200
Content-Type: application/json
```

```
{
  "openapi": "3.1.0",
  "info": {
    "title": "Turnos Odontologia API",
    "summary": "API local de turnos para demostrar el prototipo de agenda.",
    "description": "Expone crear, consultar, reprogramar y cancelar turnos sobre el servicio de dominio ya implementado. Sin autenticacion, sin datos reales y solo para loopback local.",
    "version": "0.1.0"
  },
  "paths": {
    "/clinics/{clinic_id}/appointments": {
      "post": {
        "summary": "Crear un turno",
        "operationId": "create_appointment_clinics__clinic_id__appointments_post",
        "parameters": [
          {
            "name": "clinic_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Clinic Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/AppointmentCreate"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AppointmentResponse"
                }
              }
            }
          },
          "409": {
            "description": "Recurso en conflicto",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Datos invalidos",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/clinics/{clinic_id}/appointments/{appointment_id}": {
      "get": {
        "summary": "Consultar un turno",
        "operationId": "get_appointment_clinics__clinic_id__appointments__appointment_id__get",
        "parameters": [
          {
            "name": "clinic_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Clinic Id"
            }
          },
          {
            "name": "appointment_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Appointment Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AppointmentResponse"
                }
              }
            }
          },
          "404": {
            "description": "Turno no encontrado",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "patch": {
        "summary": "Reprogramar un turno",
        "operationId": "reschedule_appointment_clinics__clinic_id__appointments__appointment_id__patch",
        "parameters": [
          {
            "name": "clinic_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Clinic Id"
            }
          },
          {
            "name": "appointment_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Appointment Id"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/RescheduleRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AppointmentResponse"
                }
              }
            }
          },
          "409": {
            "description": "Recurso en conflicto",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Datos invalidos",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "404": {
            "description": "Turno no encontrado",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/clinics/{clinic_id}/appointments/{appointment_id}/cancel": {
      "post": {
        "summary": "Cancelar un turno",
        "operationId": "cancel_appointment_clinics__clinic_id__appointments__appointment_id__cancel_post",
        "parameters": [
          {
            "name": "clinic_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Clinic Id"
            }
          },
          {
            "name": "appointment_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string",
              "title": "Appointment Id"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/AppointmentResponse"
                }
              }
            }
          },
          "404": {
            "description": "Turno no encontrado",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          },
          "422": {
            "description": "Datos invalidos",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### 3. Crear un turno (09:00-09:30)

**Solicitud**

```http
POST /clinics/demo-clinic/appointments
Content-Type: application/json

{
  "professional_id": "demo-profesional",
  "patient_id": "demo-paciente",
  "service_id": "demo-consulta",
  "chair_id": "demo-sillon",
  "start_at": "2026-12-01T09:00:00-03:00",
  "end_at": "2026-12-01T09:30:00-03:00"
}
```

**Respuesta**

```http
HTTP 201
Content-Type: application/json
```

```
{
  "id": "a931955d-ee38-4dfc-a1eb-fd22f391a162",
  "clinic_id": "demo-clinic",
  "professional_id": "demo-profesional",
  "chair_id": "demo-sillon",
  "patient_id": "demo-paciente",
  "service_id": "demo-consulta",
  "start_at": "2026-12-01T12:00:00Z",
  "end_at": "2026-12-01T12:30:00Z",
  "status": "scheduled"
}
```

### 4. Consultar el turno creado

**Solicitud**

```http
GET /clinics/demo-clinic/appointments/a931955d-ee38-4dfc-a1eb-fd22f391a162
```

**Respuesta**

```http
HTTP 200
Content-Type: application/json
```

```
{
  "id": "a931955d-ee38-4dfc-a1eb-fd22f391a162",
  "clinic_id": "demo-clinic",
  "professional_id": "demo-profesional",
  "chair_id": "demo-sillon",
  "patient_id": "demo-paciente",
  "service_id": "demo-consulta",
  "start_at": "2026-12-01T12:00:00Z",
  "end_at": "2026-12-01T12:30:00Z",
  "status": "scheduled"
}
```

### 5. Reprogramar el turno a 11:00-11:30

**Solicitud**

```http
PATCH /clinics/demo-clinic/appointments/a931955d-ee38-4dfc-a1eb-fd22f391a162
Content-Type: application/json

{
  "start_at": "2026-12-01T11:00:00-03:00",
  "end_at": "2026-12-01T11:30:00-03:00"
}
```

**Respuesta**

```http
HTTP 200
Content-Type: application/json
```

```
{
  "id": "a931955d-ee38-4dfc-a1eb-fd22f391a162",
  "clinic_id": "demo-clinic",
  "professional_id": "demo-profesional",
  "chair_id": "demo-sillon",
  "patient_id": "demo-paciente",
  "service_id": "demo-consulta",
  "start_at": "2026-12-01T14:00:00Z",
  "end_at": "2026-12-01T14:30:00Z",
  "status": "scheduled"
}
```

### 6. Conflicto de profesional (mismo profesional, 11:15-11:45)

**Solicitud**

```http
POST /clinics/demo-clinic/appointments
Content-Type: application/json

{
  "professional_id": "demo-profesional",
  "patient_id": "demo-paciente",
  "service_id": "demo-consulta",
  "chair_id": "demo-sillon",
  "start_at": "2026-12-01T11:15:00-03:00",
  "end_at": "2026-12-01T11:45:00-03:00"
}
```

**Respuesta**

```http
HTTP 409
Content-Type: application/json
```

```
{
  "code": "appointment_conflict",
  "detail": "El recurso indicado ya está ocupado en ese intervalo.",
  "resource": "professional"
}
```

### 7. Intervalo invalido (inicio igual a fin)

**Solicitud**

```http
POST /clinics/demo-clinic/appointments
Content-Type: application/json

{
  "professional_id": "demo-profesional",
  "patient_id": "demo-paciente",
  "service_id": "demo-consulta",
  "chair_id": "demo-sillon",
  "start_at": "2026-12-01T13:00:00-03:00",
  "end_at": "2026-12-01T13:00:00-03:00"
}
```

**Respuesta**

```http
HTTP 422
Content-Type: application/json
```

```
{
  "code": "invalid_appointment_interval",
  "detail": "El intervalo indicado no es válido."
}
```

### 8. Turno inexistente

**Solicitud**

```http
GET /clinics/demo-clinic/appointments/no-existe
```

**Respuesta**

```http
HTTP 404
Content-Type: application/json
```

```
{
  "code": "appointment_not_found",
  "detail": "El turno no existe en el consultorio indicado."
}
```

### 9. Cancelar el turno

**Solicitud**

```http
POST /clinics/demo-clinic/appointments/a931955d-ee38-4dfc-a1eb-fd22f391a162/cancel
```

**Respuesta**

```http
HTTP 200
Content-Type: application/json
```

```
{
  "id": "a931955d-ee38-4dfc-a1eb-fd22f391a162",
  "clinic_id": "demo-clinic",
  "professional_id": "demo-profesional",
  "chair_id": "demo-sillon",
  "patient_id": "demo-paciente",
  "service_id": "demo-consulta",
  "start_at": "2026-12-01T14:00:00Z",
  "end_at": "2026-12-01T14:30:00Z",
  "status": "cancelled"
}
```

### 10. Consultar el turno tras cancelarlo

**Solicitud**

```http
GET /clinics/demo-clinic/appointments/a931955d-ee38-4dfc-a1eb-fd22f391a162
```

**Respuesta**

```http
HTTP 200
Content-Type: application/json
```

```
{
  "id": "a931955d-ee38-4dfc-a1eb-fd22f391a162",
  "clinic_id": "demo-clinic",
  "professional_id": "demo-profesional",
  "chair_id": "demo-sillon",
  "patient_id": "demo-paciente",
  "service_id": "demo-consulta",
  "start_at": "2026-12-01T14:00:00Z",
  "end_at": "2026-12-01T14:30:00Z",
  "status": "cancelled"
}
```
