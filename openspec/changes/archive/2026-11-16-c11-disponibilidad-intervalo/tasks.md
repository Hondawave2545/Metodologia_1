# Tasks

Referencia: `specs/appointment-api/spec.md` (qué) y `design.md` (cómo). Cada tarea indica cómo se verifica
que quedó terminada.

## 1. Dominio: la disponibilidad se resuelve con la regla que ya existe

- [x] 1.1 Escribir las pruebas del dominio de la consulta de disponibilidad (intervalo libre, conflicto de profesional, conflicto de sillón, turno cancelado que no bloquea, intervalo inválido o sin zona horaria, consultorio/profesional/sillón ausente o inactivo, profesional de otro consultorio y consultorio que administra sillones sin sillón indicado); verificar que fallan antes de implementar el método
  > Evidencia: archivo nuevo `tests/test_availability_domain.py` (15 pruebas). RED: `.venv\Scripts\python.exe -m pytest tests\test_availability_domain.py -q` → **`15 failed`** con `AttributeError: 'AppointmentRepository' object has no attribute 'check_availability'`, o sea fallaron por el método inexistente y no por una expectativa mal escrita. Durante la implementación se detectó que una prueba era incorrecta (pedía un profesional de C2 contra C1, donde ese identificador sí existe) y se corrigió **antes** de volver a verde.
- [x] 1.2 Implementar el método de solo lectura de disponibilidad en el repositorio de turnos, apoyado en un helper interno de detección de conflicto extraído del que usa el alta, sin duplicar la regla de solapamiento; verificar que las pruebas de 1.1 pasan
  > Evidencia: `src/appointments.py` — se extrajo `_find_conflict(...) -> str | None` con la **misma** consulta SQL, el mismo orden (profesional antes que sillón) y la misma precedencia que ya tenía `_assert_no_conflict`, y `_assert_no_conflict` ahora se apoya en él y sigue levantando `AppointmentConflict`. Se agregó `check_availability(...)`, de solo lectura (conexión en modo lectura, sin transacción de escritura), que valida intervalo → consultorio → profesional → sillón y devuelve `"professional"`, `"chair"` o `None`. GREEN: `pytest tests\test_availability_domain.py -q` → **`15 passed`**. No hay una segunda copia de la regla de solapamiento: `Select-String "start_at <"` en `src/appointments.py` devuelve **1** coincidencia.
- [x] 1.3 Ejecutar las 18 pruebas existentes del dominio (`tests/test_appointments.py`) y verificar que siguen pasando sin haber sido modificadas
  > Evidencia: `pytest tests\test_appointments.py -q` → **`18 passed`**. `git diff -- tests/test_appointments.py` → **vacío**: el archivo no fue tocado. El refactor de `_assert_no_conflict` no cambió el comportamiento del alta, la reprogramación ni la cancelación.

## 2. API: la operación de consulta

- [x] 2.1 Escribir las pruebas HTTP de la consulta de disponibilidad (respuesta exitosa con intervalo libre, respuesta exitosa con intervalo ocupado y el recurso en conflicto, error de validación de intervalo, error de recurso no disponible, error de sillón obligatorio y ausencia de datos del paciente en la respuesta); verificar que fallan antes de implementar la ruta
  > Evidencia: archivo nuevo `tests/test_api_availability.py` (12 pruebas). RED: `pytest tests\test_api_availability.py -q` → **`12 failed`** (la ruta no existía). La prueba de no divulgación comprueba que el cuerpo no contiene ni `patient-1` ni la palabra `patient`.
- [x] 2.2 Implementar el esquema de respuesta y la ruta de consulta con sus parámetros documentados y su mapeo de errores; verificar que las pruebas de 2.1 pasan
  > Evidencia: `src/api/schemas.py` agrega `AvailabilityResponse` (`clinic_id`, `professional_id`, `chair_id`, `start_at`, `end_at`, `available`, `conflicting_resource`) y `src/api/main.py` agrega `GET /clinics/{clinic_id}/availability` con `Annotated[..., Query(description=...)]`, `responses={**_VALIDATION_RESPONSE}` y el mismo `map_domain_error`/`error_body` del resto de la API. GREEN: `pytest tests\test_api_availability.py -q` → **`12 passed`**. Nota de implementación: FastAPI 0.162 rechaza un default dentro de `Query` cuando se usa `Annotated` ("`Query` default value cannot be set in `Annotated`"), así que el parámetro opcional `chair_id` va con `= None` y la dependencia `repository` se declara antes que él.
- [x] 2.3 Documentar la operación en el `README.md` y en las referencias de la skill propia, y verificar que lo documentado coincide con lo implementado
  > Evidencia: `README.md` suma la fila en la tabla de operaciones, una sección con el ejemplo `curl` y la respuesta real, y la aclaración de que la consulta es orientativa. `.opencode/skills/api-turnos/references/contrato-http.md` suma la ruta en la tabla de rutas, la sección 4 con parámetros, respuesta y errores, y el ejemplo. Contraste contra el código: la ruta, el nombre de los parámetros, los códigos y las claves del cuerpo coinciden con lo verificado por HTTP real (sección 4.2).

## 3. Contrato y documentación

- [x] 3.1 Actualizar la prueba de arranque que fija el conjunto exacto de operaciones publicadas en el contrato, para que incluya la operación nueva sin dejar de exigir un conjunto exacto ni la ausencia de listado en la colección de turnos; verificar que la prueba sigue siendo estricta
  > Evidencia: `tests/test_api_startup.py` — `EXPECTED_OPERATIONS` suma `("/clinics/{clinic_id}/availability", "get")` y el método pasa a llamarse `test_contract_describes_exactly_the_five_operations_and_no_listing`. **Es la única prueba existente que C-11 modifica** (justificado en `design.md` D7). La aserción sigue siendo de conjunto exacto (`self.assertEqual(EXPECTED_OPERATIONS, operations)`) y la garantía de que la colección de turnos **no** tiene `GET` sigue intacta (`assertNotIn("get", contract["paths"][collection_path])` y el `assertEqual({"post"}, ...)`). Estado previo: la prueba falló con `AssertionError: Items in the second set but not the first: ('/clinics/{clinic_id}/availability', 'get')`, o sea por el número de operaciones, no por una aserción debilitada. Después del cambio: `pytest tests\test_api_startup.py -q` → **3 passed**.
- [x] 3.2 Actualizar `CHANGES.md` con el change nuevo (identificador, propósito, alcance, exclusiones, dependencias y escenarios verificables) y actualizar el estado del change C-10 como archivado
  > Evidencia: `CHANGES.md` suma la fila `C-11 | Consulta de disponibilidad de un intervalo | MVP-06 | C-05, C-10` y la sección con propósito, alcance, exclusiones, dependencias y ocho escenarios verificables. C-10 quedó como **Archivado** (2026-11-16) con su propósito "Agenda y turnos" y su dependencia real de C-05 declarada en la misma sección.

## 4. Verificación integral

- [x] 4.1 Ejecutar la suite completa con la configuración MCP del proyecto apartada y verificar que todas las pruebas pasan, confirmando que ninguna depende del servidor MCP
  > Evidencia: con el `opencode.json` del proyecto (donde vive la configuración MCP) **apartado** a un archivo temporal durante la corrida: `pytest tests -q` → **`87 passed`**; `unittest discover -s tests` → **`Ran 87 tests ... OK`**; `pytest tests -q -W error::DeprecationWarning` → **`87 passed`** (sin avisos). El `opencode.json` se restauró al terminar. `Select-String` de `mcp|context7|opencode` sobre `tests\*.py` → **0 coincidencias**.
- [x] 4.2 Verificar la operación nueva por HTTP real contra el servidor levantado, y registrar la solicitud y la respuesta en la evidencia de verificación de la API
  > Evidencia: uvicorn levantado como proceso real (`--host 127.0.0.1 --port 56966`) sobre una base propia `data/verificacion-disponibilidad.sqlite3` sembrada con el script de demo, y consultas hechas con `curl.exe` sobre TCP. Los 10 casos responded como se esperaba: intervalo libre **200** (`available: true`), crear **201**, profesional ocupado **200** (`"professional"`), sillón ocupado **200** (`"chair"`), intervalo inválido **422**, sin sillón **422** (`chair_required`), profesional inexistente **422** (`resource_unavailable`), parámetro obligatorio ausente **422** (`invalid_request`), cancelar **200** y tras cancelar la franja vuelve a estar libre **200**. Solicitudes y respuestas literales en `TPI/evidencia-verificacion-api.md` §0.1.
- [x] 4.3 Actualizar `TPI/README.md` con el estado real de los dos changes y con lo que queda pendiente de la entrega
  > Evidencia: `TPI/README.md` actualizado con la tabla de changes (C-10 archivado, C-11 archivado), la sección de pruebas, la brecha contra el mínimo de la consigna y la lista de pendientes de la entrega (video y archivo `.txt`).

## Workflow follow-up

- Archivar el change en OpenSpec una vez completadas y verificadas todas las tareas anteriores.
- Sincronizar la especificación `appointment-api` en `openspec/specs/appointment-api/spec.md` al archivar.
- Conservar la historia de los changes previos en `CHANGES.md`.
