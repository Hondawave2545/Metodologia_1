# Tasks

Referencia: `specs/appointment-api/spec.md` (qué) y `design.md` (cómo). Cada tarea indica cómo se verifica que quedó terminada.

## 1. Dependencias y entorno Python 3.14

- [x] 1.1 Declarar FastAPI, Uvicorn y las dependencias de prueba en el manifiesto Python del proyecto, con versiones fijadas, y verificar que el archivo declara las cuatro categorías que el change necesita (servidor HTTP, cliente de prueba y framework de pruebas)
- [x] 1.2 Crear un entorno con Python 3.14, instalar el manifiesto completo y verificar que la instalación termina sin errores, registrando las versiones resueltas (fastapi, uvicorn, starlette, pydantic, cliente de prueba y pytest)
- [x] 1.3 Verificar que el cliente de prueba elegido por el framework no emite avisos de deprecación al importarse, ajustando la dependencia fijada en 1.1 si el aviso aparece (ver D8 en `design.md`)

## 2. Adaptador HTTP: esquemas y mapeo de errores

- [x] 2.1 Escribir las pruebas del mapeador de errores de dominio a respuestas HTTP (conflicto de profesional o sillón → 409, intervalo inválido → 422, recurso ausente o inactivo → 422, turno inexistente → 404) que comprueben además que el cuerpo del error no contiene la identidad del paciente; verificar que estas pruebas fallan antes de implementar el mapeador
- [x] 2.2 Implementar el mapeador de errores y los esquemas de request y response, con el intervalo como fecha y hora con zona horaria explícita; verificar que las pruebas de 2.1 pasan
- [x] 2.3 Añadir al README.md la sección de instalación con los comandos exactos que se ejecutaron en 1.2, y verificar que se ejecutan tal como están escritos

## 3. Los cuatro endpoints sobre el dominio existente

- [x] 3.1 Escribir las pruebas HTTP de las cuatro operaciones (crear devuelve el turno con estado inicial; consultar devuelve el mismo turno dentro de su consultorio; reprogramar actualiza el intervalo; cancelar conserva el registro, cambia el estado a cancelado y libera profesional y sillón); verificar que fallan antes de implementar
- [x] 3.2 Implementar `POST /clinics/{clinic_id}/appointments`, `GET /clinics/{clinic_id}/appointments/{appointment_id}`, `PATCH /clinics/{clinic_id}/appointments/{appointment_id}` y `POST /clinics/{clinic_id}/appointments/{appointment_id}/cancel`, reutilizando `src/appointments.py` sin reescribir la lógica de dominio; verificar que las pruebas de 3.1 pasan
- [x] 3.3 Añadir pruebas de los casos límite del spec: conflicto de profesional y de sillón sin modificar la reserva original y sin revelar datos del paciente, intervalo inválido que no devuelve conflicto, recurso ausente o inactivo, turno inexistente y turno perteneciente a otro consultorio; verificar que pasan
- [x] 3.4 Ejecutar la suite completa del proyecto y verificar que las 18 pruebas existentes del dominio (`tests/test_appointments.py`) siguen pasando sin haber sido modificadas

## 4. Prueba automatizada de arranque

- [x] 4.1 Escribir la prueba de arranque que lanza el comando documentado con Uvicorn acotado a `127.0.0.1` sobre un puerto libre, espera a que el proceso esté listo y comprueba que el documento de contrato y la interfaz de documentación responden; verificar que la prueba falla si el comando de arranque no es reproducible
- [x] 4.2 Ampliar la prueba de arranque para comprobar que el contrato describe las cuatro operaciones y que no expone un listado de turnos; verificar que pasa
- [x] 4.3 Documentar en el README.md el comando de arranque, el acceso a Swagger y la forma de elegir un puerto libre, y verificar que el comando escrito en el README es el mismo que usa la prueba de 4.1

## 5. Script de datos ficticios

- [x] 5.1 Implementar el script de demostración que crea o verifica un consultorio, un profesional, un sillón, un paciente y un servicio con identificadores conocidos, sin borrar ni sobrescribir registros preexistentes, e informa los identificadores disponibles
- [x] 5.2 Añadir una prueba del script que lo ejecute dos veces sobre la misma base y verifique que los datos preexistentes se conservan, y que los nombres, documentos y teléfonos registrados son ficticios
- [x] 5.3 Documentar en el README.md cómo preparar los datos de demostración y qué identificadores usar en las operaciones, y verificar que los identificadores documentados coinciden con los que informa el script

## 6. Skill propia de workspace

- [x] 6.1 Crear la skill propia del proyecto con la skill creadora `skill-creator` de OpenCode, en `.opencode/skills/api-turnos/SKILL.md`, con frontmatter `name` y `description` que describa qué hace y cuándo debe dispararse, y un cuerpo con el procedimiento del ciclo de la API de turnos
  > Evidencia: la skill **ya existía** y **no se recreó** (instrucción explícita del equipo). Verificación del entregable: `Test-Path .opencode\skills\api-turnos\SKILL.md` → `True`; `Select-String` → `L2: name: API de turnos`, `L3: description: ...` (qué hace y cuándo se dispara), `L43: ## Ciclo de trabajo`, `L46: spec → test rojo → implementación mínima → test verde → suite completa → refactor`. Criterio cumplido. Lo que **faltaba** y se agregó en esta sesión: los dos archivos `references/` que la skill remite (`Test-Path` del directorio `references/` → `False` antes de esta sesión).
- [x] 6.2 Verificar que OpenCode descubre la skill: `opencode debug skill` la lista con su identificador `api-turnos` derivado de la ruta
  > Evidencia: `opencode debug skill` (raíz del proyecto) → `"name": "API de turnos"` y `"location": "<raíz del proyecto>\.opencode\skills\api-turnos\SKILL.md"` → identificador derivado de la ruta: `api-turnos`. Listada junto con las skills globales (OpenCode, engram, etc.).
- [x] 6.3 Referenciar la skill en `AGENTS.md` (y en `CLAUDE.md` si corresponde) para que el agente la use en el trabajo sobre la API de turnos, y verificar que la referencia indica la ruta exacta del archivo
  > Evidencia: nueva sección `## Skills del proyecto` en `AGENTS.md` (línea 9) y en `CLAUDE.md` (línea 9), ambos con la ruta exacta `.opencode/skills/api-turnos/SKILL.md` y el disparador. `Test-Path` sobre las tres rutas → `True` en las tres (`SKILL.md`, `references/gotchas.md`, `references/contrato-http.md`). `CLAUDE.md` exige sincronizarse con `AGENTS.md`, por eso se actualizaron los dos.
- [x] 6.4 Registrar la skill en `.atl/skill-registry.md` con su ruta y su disparador, y verificar que el registro queda consistente con lo que OpenCode lista
  > Evidencia: `.atl/skill-registry.md` línea 7 registra `api-turnos` con la ruta `.opencode/skills/api-turnos/SKILL.md`, el identificador derivado de la ruta, las dos referencias y el disparador. Contraste contra `opencode debug skill`: la ruta registrada coincide exactamente con el `location` que informa OpenCode.

## 7. Servidor MCP Context7

- [x] 7.1 Declarar el servidor Context7 en `opencode.json` en la raíz del repositorio, bajo `mcp.context7`, con `type` remoto y la URL pública del servicio, sin claves, tokens ni encabezados con credenciales
  > Evidencia: se creó `opencode.json` en la raíz con `mcp.context7 = { "type": "remote", "url": "https://mcp.context7.com/mcp", "enabled": true }`. `Select-String` de `apiKey|api_key|token|secret|password|Authorization|headers|bearer` → **0 coincidencias**. El texto original de la tarea pedía `mcp.servers.context7`; el enunciado se corrigió a `mcp.context7` (forma del esquema v1, `mcp: Record(String, Union[Local, Remote])`, y la que muestra la documentación oficial vigente) para que la tarea, el archivo y la documentación digan lo mismo. Verificación de que **ambas** formas registran y conectan el servidor en OpenCode 1.19.5: con un servidor de prueba que solo existía en el `opencode.json` del proyecto, la forma anidada `mcp.servers.servidorAnidado` y la plana `mcp.servidorPlano` aparecieron ambas en `opencode mcp list` (3 servidores).
- [x] 7.2 Verificar que `opencode.json` no está cubierto por `.gitignore` (por ejemplo con `git check-ignore opencode.json`) y que el archivo se versiona con el resto del proyecto
  > Evidencia: `git check-ignore -v opencode.json` → **exit 1** (ninguna regla coincide: **no está ignorado**). `git status --short opencode.json` → `?? opencode.json` (archivo nuevo, listo para versionarse con el resto). `.gitignore` solo cubre `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.venv/`, `venv/`, `*.db`, `*.sqlite3`, `.env`, `.env.*`, `*.key`, `.vscode/`, `.idea/`, `.DS_Store`.
- [x] 7.3 Verificar la conexión desde la raíz del proyecto con `opencode mcp list`, comprobando que Context7 figura como conectado, y documentar ese comando como forma de comprobar la configuración
  > Evidencia: `opencode mcp list` (desde la raíz del proyecto) → `● ✓ context7 connected` con `https://mcp.context7.com/mcp`. Para probar que la conexión proviene del `opencode.json` **del proyecto** y no solo del global, se agregó temporalmente un servidor `context7-proyecto-temporal` existente únicamente en ese archivo: `opencode mcp list` → `3 server(s)` listándolo; luego se quitó y volvió a `2 server(s)`. Comando documentado en `TPI/evidencia-skill-mcp.md` §2.3.
- [x] 7.4 Usar el MCP para resolver y consultar documentación pública vigente de FastAPI durante la implementación, y conservar la solicitud, la herramienta invocada y la respuesta obtenida como evidencia
  > Evidencia: `resolve-library-id` con `libraryName: "FastAPI"` → ID elegido `/websites/fastapi_tiangolo` (4160 snippets, benchmark 75.77). `query-docs` con `libraryId: /websites/fastapi_tiangolo` → devolvió la documentación oficial de handlers de excepción (`@app.exception_handler` + `JSONResponse`) y el handler por defecto de `RequestValidationError`, que **incluye `exc.body` en la respuesta** — el proyecto deliberadamente devuelve un cuerpo controlado, para no filtrar datos del paciente. Solicitud, herramienta y salida literal completa en `TPI/evidencia-skill-mcp.md` §3 y §4.
- [x] 7.5 Registrar la evidencia de 7.4 en `TPI/evidencia-skill-mcp.md`, con la solicitud, el resultado y cómo se revisó, y verificar que no quedan secciones vacías
  > Evidencia: `TPI/evidencia-skill-mcp.md` reescrito completo (secciones 1 a 6 + checklist), con la solicitud textual, la salida literal de Context7 y la tabla de revisión. `Select-String` de marcadores de plantilla `____` → **0 coincidencias**; `Select-String -CaseSensitive` de `PENDIENTE|TODO|PASSED_` → **0 coincidencias**; las 21 secciones del documento tienen contenido.

## 8. Verificación integral y documentación

- [x] 8.1 Ejecutar la suite completa con el MCP desconectado y verificar que todas las pruebas pasan, confirmando que ninguna depende del servidor MCP
  > Evidencia: (a) `Select-String` de `mcp|context7|opencode` sobre `tests\*.py`, `src\api\*.py`, `src\appointments.py` y `scripts\*.py` → **0 coincidencias**: ninguna prueba ni el código referencian el MCP. (b) Suite ejecutada con el `opencode.json` del proyecto (donde vive la configuración MCP) **apartado a un archivo temporal** durante la corrida: `.venv\Scripts\python.exe -m pytest tests -q` → `60 passed in 14.66s`; `.venv\Scripts\python.exe -m unittest discover -s tests` → `Ran 60 tests in 12.318s / OK`; `.venv\Scripts\python.exe -m pytest tests -q -W error::DeprecationWarning` → `60 passed in 12.62s`. El `opencode.json` se restauró al terminar y su contenido se verificó.
- [x] 8.2 Actualizar el README.md para que permita reproducir el alcance presentado: requisitos, instalación, configuración de ejemplo sin secretos, preparación de datos ficticios, arranque del backend, acceso a Swagger y ejecución de tests, indicando explícitamente qué está completo y qué queda pendiente
  > Evidencia: `README.md` actualizado con (i) sección nueva **"Qué está completo y qué queda pendiente"**: completo = dominio C-05, API C-10, script de datos ficticios, prueba de arranque, skill propia y MCP; pendiente = **autenticación, roles y permisos**, **frontend**, altas por API, listados/paginación/filtros, persistencia de producción, changes **C-01 a C-04** y **C-06 a C-09** del roadmap, archivado de C-10 y video/entrega del TPI; (ii) sección nueva **"Configuración de ejemplo (sin secretos)"** con el `opencode.json` literal y el comando `opencode mcp list`; (iii) requisitos, instalación, datos ficticios, arranque, Swagger y tests ya presentes y actualizados (resultado real `60 passed` = 18 del dominio + 42 de la API, verificado el 2026-11-16); (iv) tabla de estructura ampliada (`requirements.txt`, `scripts/`, `opencode.json`, `.opencode/skills/api-turnos/`) y nota de que las bases no se versionan. Verificación: `.venv\Scripts\python.exe -m pytest tests\test_api_startup.py -q` → `3 passed` (el README sigue siendo la fuente del comando de arranque: exactamente **1** línea con `uvicorn` entre los marcadores) y `openspec validate c10-api-turnos-swagger --strict` → `Change 'c10-api-turnos-swagger' is valid`.
- [x] 8.3 Verificar que el repositorio no contiene credenciales, tokens ni datos reales de pacientes, y que la base de datos de demostración no queda versionada
  > Evidencia: (a) `git ls-files` → **0** archivos `.db`/`.sqlite3` y **0** archivos `.env`/`.key`/`.pem`/`credentials` trackeados; `git check-ignore -v data/demo.sqlite3 data/verificacion-http.sqlite3` → ambos cubiertos por `.gitignore:10:*.sqlite3`; `git status --short --ignored -- data/` → `!! data/`. (b) Escaneo de credenciales sobre 45 archivos del proyecto (`api_key|secret_key|password|Bearer <token>|Authorization:|sk-…|ghp_…|PRIVATE KEY`) → **1** coincidencia: `tasks.md:50`, que es el texto del patrón de búsqueda citado en la evidencia de 7.1, no una credencial. (c) Esquema de `data/demo.sqlite3`: `patients → [clinic_id, id, active]` con la fila `('demo-clinic', 'demo-paciente', 1)` y `clinics → [id, timezone, manages_chairs]`; **ninguna columna** guarda nombre, apellido, documento, teléfono, correo, dirección ni fecha de nacimiento. (d) Escaneo de dato personal (documentos, teléfonos, correos) → **1** coincidencia: `tests/test_seed_demo_data.py:31` (`"dni"`), que es la lista de marcadores que la prueba usa justamente para **verificar que esa columna no exista**.

## Workflow follow-up

- Archivar el change en OpenSpec una vez completadas y verificadas todas las tareas anteriores.
- Sincronizar la especificación `appointment-api` en `openspec/specs/appointment-api/spec.md` al archivar.
- Actualizar el estado de C-10 en `CHANGES.md` a archivado, conservando la historia de los changes previos.
- Actualizar la tabla de estado de `TPI/README.md` para reflejar el avance real después del archivado.
