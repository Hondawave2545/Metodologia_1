# Design

## Context

C-05 (`src/appointments.py`) dejó implementado el control de solapamientos por profesional y por sillón, con
intervalos semiabiertos `[inicio, fin)` y con solo `scheduled` y `confirmed` bloqueando recursos. C-10 archivó
la capa HTTP (`src/api/`) con cuatro operaciones: crear, consultar, reprogramar y cancelar.

C-11 agrega una quinta operación, de solo lectura: consultar si un intervalo está libre. La regla que decide
eso **ya existe** en el dominio; lo que no existe es una forma de consultarla sin crear nada.

El trabajo sigue a la skill propia del proyecto (`.opencode/skills/api-turnos/SKILL.md`), que fija las reglas
que no se negocian: el dominio es la única fuente de verdad de la regla de negocio, los intervalos son
semiabiertos, los errores se construyen con texto controlado y nunca reenvían el mensaje de la excepción, y
solo hay datos ficticios.

## Decisions

### D1. La disponibilidad la resuelve el dominio, no la capa HTTP

**Qué:** `AppointmentRepository.check_availability(...)` devuelve el recurso en conflicto (`"professional"` o
`"chair"`) o `None` cuando el intervalo está libre. El dominio valida primero el intervalo, después el
consultorio, el profesional y el sillón, y por último consulta los solapamientos.

**Por qué:** la regla de solapamiento es la más crítica del producto y ya tiene una única implementación
(`_assert_no_conflict`). Una consulta de disponibilidad escrita en la capa HTTP la duplicaría, y las dos
versiones divergirían en cuanto cambiara la semántica de `[inicio, fin)` o la lista de estados que bloquean.

**Cómo:** `_assert_no_conflict` se apoya en un helper interno nuevo, `_find_conflict`, que devuelve el recurso
en conflicto en lugar de levantar la excepción. La consulta SQL, el orden de comprobación (profesional antes
que sillón) y la precedencia de errores quedan **idénticos**: es una extracción, no una reescritura. La
excepción `AppointmentConflict` se sigue levantando desde el mismo lugar, así que el alta y la reprogramación
no cambian de comportamiento.

**Alternativas consideradas:**

- Escribir la consulta de solapamiento en `src/api/`: descartada, duplicaría la regla.
- Devolver un booleano simple sin saber qué recurso bloquea: no alcanza para que una interfaz decida si
  ofrecer otro profesional u otro sillón.

### D2. Ruta y verbo

**Qué:** `GET /clinics/{clinic_id}/availability`, con `start_at`, `end_at` y `professional_id` obligatorios y
`chair_id` opcional, todos como parámetros de consulta.

**Por qué:** es una consulta sin efectos sobre el estado: un `GET` es honesto con lo que hace y no necesita
cuerpo. El consultorio va en la ruta por la misma razón que en el resto de la API: toda operación está aislada
por consultorio y así queda explícito en el contrato. Los intervalos y los recursos van en la consulta porque
son los datos que se están preguntando, no un recurso que se está creando.

La ruta **no** es la colección de turnos: la consulta no devuelve turnos, y por eso C-11 no abre un listado ni
contradice la garantía vigente de que la colección no tiene `GET`.

### D3. Los parámetros se declaran con `Query` y con descripción

**Qué:** los tres parámetros obligatorios se declaran sin valor por defecto y el opcional con `default=None`,
usando `Annotated[..., Query(description=...)]`.

**Por qué:** así el documento OpenAPI marca los obligatorios como obligatorios y publica una descripción de
cada uno, que es lo que se ve en `/docs`. El mecanismo está confirmado por la consulta al MCP Context7
registrada en `proposal.md`.

Un `datetime` sin zona horaria llega hasta el dominio, que lo rechaza con `InvalidAppointmentInterval`: el
error es `422 invalid_appointment_interval`, el mismo que devuelve el alta. Así el intervalo se valida con una
sola regla en todo el dominio.

### D4. La respuesta

**Qué:** `200` con `available` (booleano) y `conflicting_resource` (`"professional"`, `"chair"` o nulo). El
cuerpo también lleva `clinic_id`, `professional_id`, `chair_id`, `start_at` y `end_at` normalizados a UTC.

**Por qué:** un conflicto **no** es un error en esta operación: es la respuesta a la pregunta. Si el conflicto
fuera un `409`, el cliente no podría distinguir "no hay turno" de "la consulta falló" sin leer el cuerpo del
error. Con `available: false` y `conflicting_resource`, una interfaz puede ofrecer otro profesional o otro
sillón.

El cuerpo **no** incluye identificadores de turnos ni datos de pacientes: solo un booleano y el tipo de
recurso ocupado. La precedencia es la misma del alta: si el profesional está ocupado, se informa el
profesional aunque el sillón también lo esté.

### D5. Los errores reutilizan el mapeo existente

**Qué:** `422 invalid_appointment_interval`, `422 resource_unavailable` y `422 chair_required`, con los mismos
textos controlados de `DETAILS`.

**Por qué:** no hay un error nuevo que inventar. La consulta usa el mismo `map_domain_error` y el mismo
`error_body` que el resto de la API, así que ningún cliente tiene que aprender un código nuevo.

`chair_required` aparece porque el consultorio de demostración administra sillones: una consulta sin sillón
no podría responder a la pregunta que el cliente se está haciendo ("¿puedo reservar esta franja?"), y
permitirla daría un verde falso que el alta después rechazaría.

### D6. El contrato declara la operación y sus errores

**Qué:** la ruta se declara con `response_model`, `summary` y `responses={422: {"model": ErrorResponse, ...}}`.

**Por qué:** es el mismo mecanismo que ya usa el resto de la API y el que el MCP Context7 confirmó para C-10:
los errores posibles quedan publicados en `/openapi.json` y visibles en Swagger, no solo en el código.

### D7. Una prueba existente se actualiza: el conjunto de operaciones del contrato

**Qué:** `tests/test_api_startup.py` fija el conjunto **exacto** de operaciones publicadas en el contrato, con
cuatro entradas. Con C-11 el contrato tiene cinco, así que el conjunto esperado suma
`("/clinics/{clinic_id}/availability", "get")` y el nombre del método pasa a decir "las cinco operaciones".

**Por qué y por qué no es un debilitamiento:** la aserción sigue siendo de conjunto exacto (`assertEqual` con
el conjunto completo, no un subconjunto), y la garantía de que la colección de turnos **no** tiene `GET` se
conserva intacta. Lo que cambia es el número de operaciones que el contrato declara, porque C-11 agregó una.
El nombre del método se actualiza para que no describa algo que ya no es cierto.

Es la única prueba existente que C-11 modifica, y se modifica **para** que siga siendo igual de estricta.

### D8. La skill propia se aplica y se actualiza

**Qué:** el trabajo sigue el ciclo de la skill `api-turnos` (spec → test rojo → implementación mínima → test
verde → suite completa → refactor), respeta sus reglas no negociables y actualiza sus dos referencias con la
ruta nueva.

**Por qué:** la consigna del TPI exige evidencia de aplicación de la skill, no su existencia. La evidencia
concreta es que la implementación de C-11 no reimplementó la regla de solapamiento (D1), reutilizó el mapeo de
errores (D5) y sigue el ciclo de la skill.

## Risks / Trade-offs

- **[El refactor del dominio cambia el comportamiento del alta]** → `_find_conflict` conserva la consulta SQL y
  el orden exactos de `_assert_no_conflict`, y la excepción se sigue levantando desde el mismo lugar. Las 18
  pruebas del dominio se ejecutan sin modificarse y deben seguir pasando.
- **[La consulta y el alta pueden quedar desfasadas]** → es inherente a una preconsulta: entre el `GET` y el
  `POST` otro turno puede ocupar la franja. El alta sigue siendo la que valida y la que responde `409`. Se
  declara en el README y en la referencia de la skill.
- **[La consulta no sabe si el turno "entra" en la jornada]** → no hay horarios de atención en el modelo
  (eso es C-03). La consulta responde sobre un intervalo concreto, no sobre la agenda del día.
- **[Una operación más en el contrato]** → la prueba de arranque que fija el conjunto exacto de operaciones se
  actualiza (D7). Se documenta como el único test existente tocado.

## Migration Plan

No hay migración de datos: el cambio es aditivo. El esquema de la base no cambia; el método nuevo es de solo
lectura y usa la conexión en modo lectura, sin transacción de escritura.

**Orden de despliegue local:**

1. Escribir las pruebas del dominio y de la API, y verlas fallar.
2. Implementar el método del dominio y la ruta HTTP.
3. Ejecutar la suite completa.
4. Verificar la operación por HTTP real contra el servidor levantado.

**Reversión:** eliminar el método del dominio, el esquema de respuesta y la ruta. No queda estado residual.

**Al archivar:** la especificación `appointment-api` se sincroniza en `openspec/specs/appointment-api/spec.md`,
el estado de C-11 en `CHANGES.md` pasa a archivado, y el README y la skill dejan de describir la operación
como pendiente.
