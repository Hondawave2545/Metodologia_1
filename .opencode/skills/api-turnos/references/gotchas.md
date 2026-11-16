# Errores que ya se pagaron

Trampas reales del repositorio, con la evidencia de dónde están. Leé esto **antes** de escribir pruebas o
de levantar el servidor: cada punto costó tiempo en C-10.

---

## 1. El cliente de pruebas es `httpx2`, no `httpx`

`requirements.txt` declara `httpx2==2.16.0`. **No existe ninguna línea `httpx==...`** y el paquete `httpx`
no está instalado en `.venv`.

Starlette 1.10 (`starlette/testclient.py:26-44`) intenta primero `httpx2` y, si no lo encuentra, cae a
`httpx` con un `StarletteDeprecationWarning`:

```python
if TYPE_CHECKING:
    import httpx2 as httpx
else:
    try:
        import httpx2 as httpx
    except ModuleNotFoundError:  # pragma: no cover
        try:
            import httpx
        except ModuleNotFoundError:
            raise RuntimeError(
                "The starlette.testclient module requires the httpx2 package to be installed.\n"
                ...
```

Consecuencia práctica: `pip install httpx` **no** satisface Starlette 1.10 → `RuntimeError` al importar
`fastapi.testclient`, o el aviso de deprecación en cada ejecución de la suite.

Los tests no importan el cliente HTTP directamente; usan el de FastAPI:

```python
from fastapi.testclient import TestClient
```

---

## 2. En Windows, cerrá las conexiones SQLite con `contextlib.closing`

`contextlib.closing` **cierra, pero no confirma**. Por eso las escrituras de los tests llevan `commit()`
explícito; sin él, en Windows la escritura se pierde al cerrar.

En el dominio (`src/appointments.py`):

```python
with closing(self._connect()) as connection:
```

En los tests (`tests/test_api_operations.py`, `tests/test_seed_demo_data.py`):

```python
with closing(sqlite3.connect(self.repository.database_path)) as connection:
    connection.execute(
        "UPDATE chairs SET active = 0 WHERE clinic_id = ? AND id = ?",
        (clinic_id, chair_id),
    )
    connection.commit()
```

Ojo también con `sqlite3.connect(...)`: por defecto usa `check_same_thread=True` y el dominio abre con
`isolation_level=None` (autocommit), `timeout=10`, `PRAGMA journal_mode = WAL` y `BEGIN IMMEDIATE`.

---

## 3. `status.HTTP_422_UNPROCESSABLE_ENTITY` está deprecado

Starlette 1.10 lo marca como obsoleto y sugiere `HTTP_422_UNPROCESSABLE_CONTENT` (mismo valor `422`).
El proyecto usa la constante nueva:

```python
status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
```

Trampa extra: **`fastapi.status` no es un submódulo importable** (`import fastapi.status` →
`ModuleNotFoundError`). Lo que existe es `from fastapi import status`, que en realidad reexporta
`starlette.status`.

---

## 4. Cómo se construye el cliente de prueba

```python
self.app = create_app()
self.app.dependency_overrides[get_repository] = lambda: self.repository
self.addCleanup(self.app.dependency_overrides.clear)
self.client = TestClient(self.app)
```

- **No** se pasa `base_url`: el default de Starlette es `http://testserver`.
- **No** se usa `ASGITransport`: `TestClient` usa su propio transporte.
- `dependency_overrides` evita por completo la base de datos real en las pruebas de operaciones.
- La variable de entorno del código es `APPOINTMENTS_DB_PATH`
  (`ENVIRONMENT_VARIABLE` en `src/api/config.py`); default `data/demo.sqlite3`.
- **Cache de repositorios**: `src/api/dependencies.py` cachea por `str(path.resolve())`. Existe
  `clear_repository_cache()`, pero ningún test lo llama: si cambiás `APPOINTMENTS_DB_PATH` a un path ya
  usado en el proceso, se reutiliza el repositorio cacheado.

---

## 5. La prueba de arranque lee el comando del `README.md`

`tests/test_api_startup.py` parte el `README.md` por los marcadores:

```python
START_MARKER = "<!-- comando-de-arranque: inicio -->"
END_MARKER = "<!-- comando-de-arranque: fin -->"
```

y se queda **solo con las líneas que contengan `"uvicorn"`**:

```python
commands = [line for line in lines if "uvicorn" in line]
if len(commands) != 1:
    raise AssertionError(
        f"Se esperaba un unico comando de arranque en el README.md, hay {len(commands)}."
    )
```

Trampas:

- **Mencionar `uvicorn` dos veces entre los marcadores rompe la prueba**, aunque sea en prosa.
- El puerto se sustituye con `re.sub(r"--port\s+\d+", f"--port {self.port}", command)` sobre el comando
  completo: `"--port 8000"` son dos argumentos separados y el reemplazo tiene que atravesar el espacio.
- El intérprete se reemplaza con `command.split()`: el comando del `README.md` **no puede** llevar comillas
  ni espacios dobles dentro de un argumento.
- Aserciones sobre el comando: debe contener `"uvicorn"`, `"src.api.main:app"` y `"--host 127.0.0.1"`.
- El puerto libre se elige con un socket efímero (`bind(("127.0.0.1", 0))`): hay una carrera TOCTOU
  mínima entre cerrarlo y que uvicorn lo tome.
- Si el proceso muere, el mensaje de aserción incluye `process.returncode`; si no responde, incluye la
  salida, **pero esa salida siempre queda vacía** porque el `stdout` del pipe nunca se lee.

---

## 6. `src` es un *namespace package*: el CWD importa

`src/` **no** tiene `__init__.py` (solo `src/appointments.py` y `src/api/__init__.py`).

```bash
.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

solo funciona con el **directorio de trabajo en la raíz del proyecto**. La prueba de arranque lo garantiza
con `cwd=PROJECT_ROOT`. Ejecutar el script desde otro directorio da
`ModuleNotFoundError: No module named 'src'`.

---

## 7. Orden de validación: los recursos se comprueban **antes** que el conflicto

En `create_appointment` el orden es: intervalo → consultorio → profesional → paciente → servicio → sillón →
conflicto.

Consecuencia real: un request con **paciente inexistente y además el slot ocupado** devuelve
`422 resource_unavailable`, **no** `409`. El `409` solo aparece cuando todos los recursos existen.

---

## 8. Casos que no devuelven lo que uno espera

| Situación | Respuesta real | Por qué |
|---|---|---|
| Cancelar dos veces | `404 appointment_not_found` | el `UPDATE` filtra `status IN ('scheduled','confirmed')`; `rowcount == 0` → `AppointmentNotFound` |
| Reprogramar un turno cancelado | `422 resource_unavailable` | `row["status"] not in ACTIVE_STATUSES` → `ResourceUnavailable("Appointment is not active")` |
| `GET` sobre la colección | `405 {"detail":"Method Not Allowed"}` | no hay listado, y no es un error de dominio |
| Ruta inexistente | `404 {"detail":"Not Found"}` | no es un error de dominio |

Solo `AppointmentError` y `RequestValidationError` tienen handler propio. Todo lo demás usa los handlers
por defecto de FastAPI/Starlette, con la forma `{"detail": ...}`.

---

## 9. La forma del cuerpo de error

- Cuando hay recurso en conflicto, el JSON tiene **tres** claves: `code`, `detail`, `resource`.
- Cuando no hay recurso, la clave `resource` **no existe** (no es `null`):

```json
{"code":"resource_unavailable","detail":"El recurso indicado no existe, está inactivo o pertenece a otro consultorio."}
```

- `ErrorResponse` en `responses={...}` del decorador es **solo documentación**: no valida el cuerpo en
  runtime. El cuerpo real lo arma `error_body()` en `src/api/errors.py`.

---

## 10. `map_domain_error` hace `raise error` si la excepción no está mapeada

Una subclase nueva de `AppointmentError` sin entrada en `_MAPPINGS` se traduce en **HTTP 500**, no en
422/409. Si agregás una excepción de dominio, agregá su mapeo en `src/api/errors.py` **en el mismo cambio**.

El orden de `_MAPPINGS` importa: se evalúa con `isinstance` y `AppointmentConflict` va primero.

---

## 11. Otros detalles que muerden

- `extra="forbid"` en `AppointmentCreate` y `RescheduleRequest`: un campo extra (por ejemplo
  `datos_del_paciente`) dispara `422 invalid_request`.
- `response_model=AppointmentResponse` **filtra** la respuesta: solo salen los 9 campos declarados. Un
  campo nuevo del dominio no aparece sin tocar el schema.
- No hay middleware: `app.user_middleware == []`. **Sin CORS**, sin request-id, sin logging.
- `clinic_id` no se valida: se usa tal cual como filtro SQL; el aislamiento depende de que exista la fila.
- La base de demo (`data/demo.sqlite3`) está en disco pero **ignorada por git** (`.gitignore` cubre
  `*.db` y `*.sqlite3`).
- El handler de `RequestValidationError` devuelve un cuerpo controlado, **no** el `exc.body` que devuelve
  FastAPI por defecto: eso es deliberado, para que un body con datos del paciente no se refleje en la
  respuesta de error.
