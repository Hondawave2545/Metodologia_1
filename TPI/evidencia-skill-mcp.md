# Evidencia: skill propia y servidor MCP

Registro de la aplicación concreta de la **skill propia** y del **servidor MCP** al proyecto, exigida por la
consigna del TPI (apartado 4: "Skill propia y servidor MCP").

> Regla de la consigna: *"Tener la skill y el MCP instalados o mostrar sus nombres en una lista no demuestra su
> aplicación"*. Se registra **qué se pidió, qué se ejecutó, qué se obtuvo y cómo se revisó**.

Fecha de carga: 2026-11-16
Change(s) en el que se aplicó: `C-10` — `c10-api-turnos-swagger` (API local de turnos con Swagger)
Integrante(s) responsable(s): 1 integrante (el nombre y apellido están pendientes de completar en
`TPI/entrega-borrador.txt`; no se inventa aquí)

---

## 1. Skill propia

### 1.1. Qué necesidad resuelve

El proyecto tiene una capa HTTP (`src/api/`) sobre un dominio ya archivado y verificado
(`src/appointments.py`), y ese desacople genera tres riesgos concretos que una skill estandariza:

1. **Que alguien reescriba la regla de negocio en la capa HTTP.** La regla de solapamiento, los estados que
   bloquean y el aislamiento por consultorio viven en el dominio; duplicarla en `src/api/` crea dos fuentes
   de verdad para la regla más crítica del producto.
2. **Que un agente repita errores de tooling ya pagados**: el cliente de pruebas es `httpx2` y no `httpx`;
   en Windows hay que cerrar las conexiones SQLite con `contextlib.closing`; y
   `status.HTTP_422_UNPROCESSABLE_ENTITY` está deprecado en Starlette 1.10.
3. **Que el contrato HTTP se desincronice del spec**: las rutas, los códigos 409/422/404 y el mapeo desde los
   errores del dominio están normados en
   `openspec/changes/c10-api-turnos-swagger/specs/appointment-api/spec.md`.

La skill `api-turnos` cubre el ciclo completo sobre esa capa: qué leer antes de tocar nada, qué reglas no se
negocian, cómo se trabaja (spec → test rojo → implementación mínima → test verde → suite completa →
refactor), cómo se verifica, y dónde están las trampas y el contrato.

### 1.2. Cómo la crearon

| Dato | Valor |
|---|---|
| Skill creadora utilizada | `skill-creator` de OpenCode (`~/.config/opencode/skills/skill-creator/SKILL.md`) |
| Ruta en el repositorio | `.opencode/skills/api-turnos/SKILL.md` |
| Nombre de la skill | Frontmatter `name: API de turnos`; identificador derivado de la ruta: `api-turnos` |
| Referencias / archivos auxiliares | `.opencode/skills/api-turnos/references/gotchas.md` y `.opencode/skills/api-turnos/references/contrato-http.md` |

El proceso:

1. Se creó el `SKILL.md` en `.opencode/skills/api-turnos/` con `skill-creator`, con frontmatter `name` y
   `description` que describen **qué hace** (API HTTP de turnos: endpoints, esquemas, mapeo de errores,
   pruebas, script de demo, pruebas de arranque) y **cuándo se dispara** (toda tarea que toque la API de
   turnos, Swagger, `/docs`, `/openapi.json`, el contrato HTTP de citas o los tests de FastAPI, aunque no se
   nombre la skill).
2. El cuerpo fijó las reglas no negociables (dominio intocable, intervalos semiabiertos `[inicio, fin)`,
   errores sin datos del paciente, solo datos ficticios, sin autenticación/listados/altas) y el ciclo de
   trabajo.
3. **En esta sesión (2026-11-16) la skill NO se recreó** — ya existía y OpenCode la detectaba. Lo que sí se
   hizo fue completar lo que le faltaba: los dos archivos `references/` que el propio `SKILL.md` remitía y que
   **no existían** en el repositorio (`Test-Path` → `False` para el directorio `references/`). Se
   reconstruyeron desde el código y las pruebas reales, no desde memoria.

### 1.3. Cómo la adaptaron

- **Convención del repositorio**: todo en español rioplatense, sin emojis, con los nombres técnicos del
  código intactos (`src/appointments.py`, `DETAILS`, `ACTIVE_STATUSES`).
- **Semántica de agenda**: las dos referencias repiten explícitamente que los intervalos son semiabiertos
  `[inicio, fin)` y que solo `scheduled` y `confirmed` bloquean profesional y sillón.
- **Datos ficticios**: `references/contrato-http.md` documenta los identificadores `demo-*` y aclara que el
  paciente es un id opaco (no hay columna para nombre, documento ni teléfono).
- **Reglas de OpenSpec**: la skill obliga a leer el spec del change y a confirmar el estado con
  `openspec status --change "<change>" --json` en vez de de memoria, y a no archivar sin pedido explícito.
- **Verificación acotada**: la skill fija los dos comandos de suite (`pytest tests -q` y
  `unittest discover -s tests`) y advierte que `tests/test_appointments.py` (dominio de C-05) no debe
  modificarse.
- **Documentación y evidencia**: cierra pidiendo actualizar `README.md` si cambió el contrato y registrar la
  evidencia en `TPI/evidencia-skill-mcp.md` cuando se usó el MCP.

### 1.4. Dónde quedó integrada y referenciada

| Lugar | Referencia |
|---|---|
| Archivo de la skill | `.opencode/skills/api-turnos/SKILL.md` |
| Referenciada en `AGENTS.md` | Sección `## Skills del proyecto` (línea 9): ruta exacta `.opencode/skills/api-turnos/SKILL.md`, disparador y las dos referencias |
| Referenciada en `CLAUDE.md` | Sección `## Skills del proyecto` (línea 9): misma ruta y disparador. `CLAUDE.md` exige mantener sincronizadas estas instrucciones con `AGENTS.md`, por eso se actualizaron las dos |
| Registrada en `.atl/skill-registry.md` | Línea 7: entrada `api-turnos` con la ruta, el identificador derivado de la ruta, las dos referencias y el disparador |

### 1.5. Criterios de revisión de la skill

La skill no se acepta por existir. Se revisa contra:

| Criterio | Cómo se verifica | Resultado |
|---|---|---|
| OpenCode la descubre | `opencode debug skill` | Lista `"name": "API de turnos"` con `"location": "...\.opencode\skills\api-turnos\SKILL.md"`. El identificador derivado de la ruta es `api-turnos`. |
| Las referencias que nombra existen | `Test-Path` sobre las dos rutas | `True` en ambas (antes de esta sesión: `False`, el directorio `references/` no existía) |
| Las reglas que afirma son las del código | Contraste contra el código | `httpx2==2.16.0` en `requirements.txt` y `httpx` ausente; `contextlib.closing` en `src/appointments.py` y en los tests; `status.HTTP_422_UNPROCESSABLE_CONTENT` en `src/api/main.py` con `HTTP_422_UNPROCESSABLE_ENTITY` deprecado en Starlette 1.10. Las tres afirmaciones de la skill se confirman en el código. |
| El contrato documentado coincide con la implementación | Contraste contra `src/api/main.py`, `src/api/errors.py` y las pruebas | Las 4 rutas, los códigos de éxito (`201` en crear; `200` en las otras tres) y el mapeo 409/422/404 coinciden con lo implementado y con lo que fijan las pruebas |
| Es referenciada donde el agente la va a leer | Búsqueda en `AGENTS.md` y `CLAUDE.md` | Presente en ambas, con la ruta exacta |
| El registro es consistente con lo que lista OpenCode | Contraste `.atl/skill-registry.md` vs `opencode debug skill` | La ruta registrada coincide exactamente con el `location` que informa OpenCode |

---

## 2. Servidor MCP

### 2.1. Cuál se instaló o conectó

| Dato | Valor |
|---|---|
| Servidor MCP | **Context7** (documentación pública y vigente de librerías) |
| Configuración en el repositorio | `opencode.json` en la raíz del proyecto |
| Transporte / URL | Remoto HTTP — `https://mcp.context7.com/mcp` |
| Autenticación | **Sin credenciales.** El archivo no declara claves, tokens ni encabezados con credenciales |
| Costo | Servicio público de Context7, sin plan pago ni claves en el repositorio |
| Permisos que otorga | Consultar documentación de librerías (`resolve-library-id` y `query-docs`). No da acceso a la base, a la red interna ni a datos del proyecto |

Contenido real de `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true
    }
  }
}
```

> **Nota sobre la ruta de la clave.** La forma usada es `mcp.context7`: el esquema de configuración de OpenCode
> v1 declara los servidores **directamente** bajo `mcp` (`mcp: Record(String, Union[Local, Remote])`), que es
> también la forma que muestra la documentación oficial vigente. La forma anidada `mcp.servers.context7`
> **también** registra y conecta el servidor en OpenCode 1.19.5 (verificado el 2026-11-16 con un servidor de
> prueba que solo existía en el `opencode.json` del proyecto); se conserva la forma del esquema porque es la
> que ya está implementada en el repositorio.

### 2.2. Qué capacidades aporta

- `resolve-library-id`: resuelve el nombre de una librería al identificador de Context7, con puntaje de
  cobertura y benchmark.
- `query-docs`: trae la documentación oficial vigente de esa librería, con ejemplos de código.

En este proyecto sirve para contrastar decisiones de la capa HTTP contra la documentación oficial de
FastAPI en lugar de confiar en la memoria del modelo.

### 2.3. Cómo se comprobó la conexión y el uso de una herramienta real

**Prueba de conexión**, desde la raíz del proyecto:

```
$ opencode mcp list
┌─  MCP Servers
│
●  ✓ context7 connected
│      https://mcp.context7.com/mcp
│
●  ✓ engram connected
│      engram mcp
│
└─  2 server(s)
```

**Prueba de que la conexión viene del archivo del proyecto y no solo de la configuración global.** Se
agregó temporalmente un servidor `context7-proyecto-temporal` que existía **únicamente** en el
`opencode.json` del proyecto:

```
$ opencode mcp list
●  ✓ context7 connected
●  ✓ engram connected
●  ✓ context7-proyecto-temporal connected
       https://mcp.context7.com/mcp
└─  3 server(s)
```

El servidor temporal apareció, lo que prueba que el archivo de la raíz del proyecto se carga y es efectivo.
Se quitó después y la lista volvió a `2 server(s)`.

**Prueba de uso real de una herramienta:** ver la sección 3 (Uso 1).

---

## 3. Solicitud

### Uso 1 — fecha: 2026-11-16 (MCP Context7 sobre FastAPI)

- **Herramienta / skill utilizada:** MCP Context7 — `resolve-library-id` y luego `query-docs`
- **Solicitud exacta (textual):**

  ```
  resolve-library-id
    libraryName: FastAPI
    query: FastAPI HTTPException custom exception handlers status codes and TestClient

  query-docs
    libraryId: /websites/fastapi_tiangolo
    query: custom exception handler returning JSONResponse with custom status code and controlled body,
           HTTPException status codes 409 422 404
  ```

- **Contexto:** change `C-10`, capa HTTP `src/api/`. La pregunta era acotada a propósito: contrastar con la
  documentación oficial el mecanismo que usa el proyecto para traducir errores del dominio a respuestas
  HTTP (un `@app.exception_handler` por tipo de excepción, con cuerpo controlado) y el tratamiento de
  `RequestValidationError`, que es la única fuente de `422 invalid_request`.

---

## 4. Resultado

### Uso 1 — fecha: 2026-11-16

**a) `resolve-library-id`**

```
Available Libraries:

- Title: FastAPI
  Context7-compatible library ID: /websites/fastapi_tiangolo
  Description: FastAPI is a modern, high-performance web framework for building APIs with Python, known for
  its speed, ease of use, and automatic interactive documentation based on OpenAPI standards.
  Code Snippets: 4160
  Source Reputation: High
  Benchmark Score: 75.77
```

Se eligieron los dos candidatos con más cobertura: `/websites/fastapi_tiangolo` (4160 snippets, benchmark
75.77) y `/websites/fastapi_tiangolo_reference` (1512 snippets, benchmark 63.17). Se usó el primero.

**b) `query-docs`** — respuesta (extracto literal de las secciones relevantes):

```
### Handle RequestValidationError and include body in response

Source: https://fastapi.tiangolo.com/tutorial/handling-errors/

Use this handler to log or return the invalid request body during development. The handler returns a 422
response containing both the validation errors and the received body.

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

### Install custom exception handler with @app.exception_handler()

Source: https://fastapi.tiangolo.com/tutorial/handling-errors/

    @app.exception_handler(UnicornException)
    async def unicorn_exception_handler(request: Request, exc: UnicornException):
        return JSONResponse(
            status_code=418,
            content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
        )

### Override the default exception handlers

FastAPI has some default exception handlers.
These handlers are in charge of returning the default JSON responses when you raise an HTTPException and when
the request has invalid data. You can override these exception handlers with your own.
```

**Aporte concreto al change:** la documentación oficial confirma que el mecanismo usado por el proyecto es el
correcto y el soportado — un `@app.exception_handler` por tipo de excepción, con `JSONResponse` y código
propio. También confirma que **el comportamiento por defecto de FastAPI para `RequestValidationError`
incluye `exc.body` en la respuesta**. El proyecto deliberadamente **no** lo hace: `src/api/main.py` devuelve
un cuerpo controlado `{"code": "invalid_request", "detail": "La solicitud no cumple el contrato de la API."}`.
La documentación oficial valida esa decisión: incluir el body permitiría reflejar en la respuesta de
error los datos que el cliente envió, lo que contradice la regla de "errores sin datos del paciente" de
`AGENTS.md` y de la skill `api-turnos`. Se dejó registrado en `references/gotchas.md` (punto 11).

---

## 5. Cómo lo revisé

### Uso 1

| Aspecto | Verificación | Resultado |
|---|---|---|
| ¿La salida resuelve lo pedido? | Se buscó el mecanismo de handlers de excepción y el de `RequestValidationError` | Sí: devolvió `@app.exception_handler` + `JSONResponse` + el handler por defecto de `RequestValidationError` con `exc.body` |
| ¿Es consistente con el spec del change? | Se contrastó con `specs/appointment-api/spec.md` (escenario "Mapeo explícito de los errores del dominio" y la exigencia de no identificar al paciente) | Sí: el spec exige un error no revelador; el handler controlado del proyecto lo cumple y la documentación confirma que la variante por defecto no lo haría |
| ¿Hay datos ficticios y sin secretos? | Se revisó el cuerpo de la respuesta de Context7 | No hay datos de pacientes, ni claves, ni tokens: es documentación pública de FastAPI |
| ¿Qué prueba lo respalda? | `tests/test_api_contract.py` (cuerpo del error sin texto de la excepción) y `tests/test_api_operations.py` (campo `resource` ausente cuando no aplica) | `60 passed` en la suite completa de C-10, registrada en `TPI/README.md` |
| ¿La herramienta se usó de verdad? | Se guardó la salida literal, no un resumen | Sí: la respuesta de Context7 está volcada textualmente arriba |

---

## 6. Aporte al proyecto

| Incorporación | Change | Aporte concreto |
|---|---|---|
| Skill propia | C-10 | `.opencode/skills/api-turnos/SKILL.md` más las dos referencias que le faltaban (`references/gotchas.md`, `references/contrato-http.md`). El agente que retome la API de turnos tiene el contrato, las trampas y el ciclo de trabajo sin redescubrirlos, y `AGENTS.md` / `CLAUDE.md` / `.atl/skill-registry.md` apuntan a la ruta exacta. |
| MCP | C-10 | `opencode.json` en la raíz con Context7 como servidor remoto **sin credenciales**, verificable con `opencode mcp list` desde la raíz del proyecto. La primera consulta real (documentación oficial de FastAPI) validó el diseño del handler de `RequestValidationError` y dejó anotado en las referencias por qué el proyecto no devuelve `exc.body`. |

---

## Checklist antes de entregar

- [x] La skill propia existe en el repositorio y está referenciada para que el agente la use
      (`AGENTS.md`, `CLAUDE.md`, `.atl/skill-registry.md`, con ruta exacta).
- [x] El MCP tiene configuración documentada y reproducible, sin credenciales
      (`opencode.json` + `opencode mcp list`).
- [x] Hay al menos un uso real de cada uno con solicitud, herramienta, resultado y aporte al change.
- [x] La evidencia está llena (no quedan secciones vacías ni marcadores de plantilla sin completar).
- [x] Los pendientes y límites están declarados como tales (integrante sin nombre completo; `TPI/README.md`
      mantiene la lista de lo que falta).
