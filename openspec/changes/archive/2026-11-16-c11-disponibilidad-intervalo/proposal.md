# Proposal

## Why

Hoy la API solo permite agendar a ciegas: el cliente envía el alta y, si la franja está ocupada, descubre el
problema recién cuando la respuesta es `409`. Cualquier pantalla de agenda necesita saber **antes** si una
franja está libre, para no hacer perder el turno al paciente ni enviarlo a un error. La consulta de
disponibilidad es la operación que precede a toda reserva, y hoy no existe.

## What Changes

- Agregar una operación de solo lectura `GET /clinics/{clinic_id}/availability`, con `start_at`, `end_at` y
  `professional_id` obligatorios y `chair_id` opcional.
- La respuesta es `200` con `available` y `conflicting_resource` (`"professional"`, `"chair"` o nulo). Un
  conflicto **no** es un error en esta operación: es el resultado de la consulta. El cuerpo no incluye ningún
  turno, ningún identificador de turno ni dato de paciente.
- El solapamiento se resuelve en el dominio, reutilizando la detección de conflictos que ya usa el alta. No se
  duplica la regla de negocio en la capa HTTP.
- Errores con el mismo mapeo ya existente: `422 invalid_appointment_interval` (intervalo inválido o sin zona
  horaria), `422 resource_unavailable` (consultorio, profesional o sillón inexistente, inactivo o ajeno al
  consultorio) y `422 chair_required` (consultorio que administra sillones y la consulta no indica sillón).
- El contrato declara la operación y sus errores en el documento OpenAPI, con los mismos parámetros `status_code`
  y `responses` que usa el resto de la API.
- **No** hay listado de turnos, ni altas de recursos, ni autenticación, ni paginación, ni persistencia de
  producción, ni definición de horarios de atención.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `appointment-api`: se agrega el requisito de consulta de disponibilidad de un intervalo y se ajusta el
  requisito de descubrimiento del contrato, que deja de exigir exactamente cuatro operaciones.

## Impact

- **Código previsto:**
  - `src/appointments.py`: un método público de solo lectura, `check_availability`, que devuelve el recurso en
    conflicto o `None`. Se apoya en un helper interno de detección de conflicto extraído del que ya usa el
    alta, para que exista **una sola** definición de la regla de solapamiento.
  - `src/api/schemas.py`: el esquema de respuesta de la consulta.
  - `src/api/main.py`: la nueva ruta y su mapeo de errores.
- **Pruebas previstas:** dos archivos nuevos, uno del dominio y uno de la API, más la actualización de
  `tests/test_api_startup.py`, que fija el conjunto exacto de operaciones publicadas en el contrato.
- **Documentación prevista:** `README.md`, `CHANGES.md`, la especificación `appointment-api` (al archivar) y las
  referencias de la skill propia `api-turnos`.
- **Dependencias previstas:** ninguna nueva. Se sigue usando FastAPI, Uvicorn, `httpx2` y pytest fijados en
  `requirements.txt`.
- **Dependencia funcional:** C-05 (el dominio que aporta la regla de solapamiento) y C-10 (la capa HTTP, el
  contrato y las convenciones). No depende de C-01–C-04 ni de C-06–C-09, y no los reemplaza.
- **Seguridad:** sin autenticación, sin credenciales y sin datos reales. La consulta no devuelve turnos ni
  pacientes: solo un booleano y el tipo de recurso ocupado.

## Consulta al MCP Context7 que fijó una decisión de este change

**Qué se pidió** (servidor MCP Context7, remoto, sin credenciales):

```
resolve-library-id
  libraryName: FastAPI
  query: FastAPI response_model status_code 201 POST and OpenAPI responses documentation

query-docs
  libraryId: /websites/fastapi_tiangolo
  query: query parameters: required and optional parameters with datetime type, Query() with description,
         how they appear in OpenAPI
```

**Qué devolvió** (extracto literal de la documentación oficial devuelta por el MCP):

- *Query Params*: "When you declare a default value for non-path parameters ... then it is not required. If you
  don't want to add a specific value but just make it optional, set the default as `None`. But when you want to
  make a query parameter required, you can just not declare any default value".
- *Query Params Str Validations*: `q: str | None = Query(default=None, title="Query string", description="...")`
  — "The `Query` version declares it explicitly as being a query parameter", y "The description appears in the
  generated OpenAPI schema and documentation UIs".
- *Query Params Models*: la alternativa con `Annotated[DateRange | None, Query()] = None` para modelos de
  parámetros.

**Qué decisión del change cambió.** El borrador inicial declaraba los cuatro parámetros como argumentos de
función sueltos (`start_at: datetime`, `end_at: datetime`, `professional_id: str`, `chair_id: str | None =
None`), sin `Query()` ni `Annotated`. Eso documentaba mal el contrato: en el esquema OpenAPI los parámetros
obligatorios no quedaban marcados como tales y ninguno llevaba descripción, así que `/docs` mostraba cuatro
cajas de texto sin explicar qué significaba `start_at`. La consulta mostró el mecanismo correcto —
`Annotated[..., Query(description=...)]`, con los obligatorios sin default y el opcional con `default=None` —
y ese mecanismo es el que quedó implementado (D3 en `design.md`). La misma consulta confirmó que la forma de
declarar respuestas adicionales con su modelo en el documento (`responses={...: {"model": ...}}`) es la que ya
usa el resto de la API, así que la nueva operación se declara igual (D6).
