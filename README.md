# Turnos Odontología

Sistema de gestión de turnos y agenda de pacientes para consultorios odontológicos, pensado para el mercado argentino.
Trabajo de integración de Metodología I (Spec-Driven Development con OpenSpec y Active Stack).

> **Estado:** prototipo de dominio más una API local de demostración.
> - **Change archivado y verificado:** *crear turnos sin solapamientos* (profesional y sillón) — `src/appointments.py`, 18 pruebas.
> - **Change archivado y verificado (C-10):** *agenda y turnos* — la API local con Swagger sobre ese dominio, `src/api/`, 42 pruebas. Secuencia real por HTTP registrada en `TPI/evidencia-verificacion-api.md`.
>
> No hay autenticación, roles ni frontend. La API está limitada a loopback y a datos ficticios.
> El detalle de alcance está en [Qué está completo y qué queda pendiente](#qué-está-completo-y-qué-queda-pendiente).

## Qué está completo y qué queda pendiente

### Completo y verificado

| Elemento | Estado | Evidencia |
|---|---|---|
| Dominio de turnos sin solapamientos (C-05) | **completo y archivado** | `src/appointments.py`, 18 pruebas en `tests/test_appointments.py` (sin modificar) |
| Agenda y turnos por HTTP (C-10) | **completo y archivado** | `src/api/`, 42 pruebas; secuencia real por HTTP en `TPI/evidencia-verificacion-api.md`; archivado en `openspec/changes/archive/2026-11-16-c10-api-turnos-swagger/` |
| Consulta de disponibilidad de un intervalo (C-11) | **completo y archivado** | `GET /clinics/{clinic_id}/availability`, 27 pruebas nuevas; secuencia real por HTTP en `TPI/evidencia-verificacion-api.md` §0.1; archivado en `openspec/changes/archive/2026-11-16-c11-disponibilidad-intervalo/` |
| Script de datos ficticios | **completo** | `scripts/seed_demo_data.py`, idempotente, 5 pruebas |
| Prueba automatizada de arranque | **completo** | `tests/test_api_startup.py` levanta el comando documentado y verifica `/docs` y `/openapi.json` |
| Skill propia del proyecto | **completo** | `.opencode/skills/api-turnos/SKILL.md` (+ `references/`), referenciada en `AGENTS.md` y `CLAUDE.md` |
| Servidor MCP Context7 | **completo** | `opencode.json` en la raíz, remoto y **sin credenciales**; evidencia en `TPI/evidencia-skill-mcp.md` |

### Pendiente

| Elemento | Por qué sigue pendiente |
|---|---|
| **Autenticación, roles y permisos** | Fuera del alcance de C-10 por decisión explícita: la API escucha solo en loopback, sin credenciales ni datos reales. Requiere su propio change (C-01) y revisión de datos sensibles. |
| **Frontend / interfaz web** | No existe ninguna. C-10 expone únicamente la API y su documentación Swagger. |
| **Alta de recursos por API** | Consultorios, profesionales, sillones, pacientes y servicios no se crean por HTTP: hoy se preparan con el script de demo. |
| **Listado, paginación, filtros y reportes** | No implementados: el contrato expone las cuatro operaciones de un turno más la consulta de disponibilidad, que no devuelve turnos. |
| **Persistencia de producción** | Sigue siendo SQLite local; el motor de producción está abierto en el roadmap. |
| **C-01 a C-04** (consultorio y zona horaria, profesionales/servicios/sillones, disponibilidad, pacientes con datos mínimos) | Changes del roadmap sin artefactos en `openspec/`. C-10 es una rama técnica de demostración y no los reemplaza. |
| **C-06 a C-09** (estados del turno, auditoría, WhatsApp, piloto) | Changes del roadmap sin artefactos en `openspec/`. C-08 es la puerta de decisión del MVP. |
| **Video y archivo de entrega del TPI** | Guion en `TPI/guion-video.md`; modelo en `TPI/entrega-borrador.txt` con campos sin completar. |

El detalle por change está en `CHANGES.md`.

## Requisitos

- Python 3.14 (verificado con 3.14.8).
- Git.

El dominio de `src/appointments.py` no usa dependencias externas: solo la librería estándar (`sqlite3`, `datetime`, `unittest`).
Las dependencias de la API están declaradas en `requirements.txt` y fijadas a versiones exactas.

## Instalar

```bash
git clone https://github.com/Hondawave2545/Metodologia_1.git
cd Metodologia_1

python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

En Linux o macOS, activating el entorno es `source .venv/bin/activate` y los comandos siguientes son `python ...`.

Instalación verificada con Python 3.14.8, que resolvió:

| Paquete | Versión |
|---|---|
| fastapi | 0.162.7 |
| uvicorn[standard] | 0.54.0 |
| starlette | 1.10.0 |
| pydantic | 2.14.3 |
| httpx2 | 2.16.0 |
| pytest | 9.2.0 |

> El cliente de pruebas es `httpx2`: starlette 1.10 declara `httpx` obsoleto para `starlette.testclient` y recomienda `httpx2`. Con `httpx2` la suite corre sin avisos de deprecación.

## Ejecutar los tests

```bash
.venv\Scripts\python.exe -m pytest tests -v
```

O, sin depender de pytest:

```bash
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Resultado verificado el 2026-11-16, con la configuración MCP del proyecto apartada: `60 passed`
— 18 del dominio (C-05) y 42 de la API (C-10). La suite **no depende del servidor MCP**: ni los tests
ni `src/` lo mencionan.

## Configuración de ejemplo (sin secretos)

El único archivo de configuración del proyecto es `opencode.json`, en la raíz. Declara el servidor MCP
Context7, que sirve para consultar documentación pública de librerías durante el desarrollo. **No lleva
claves, tokens ni encabezados con credenciales, y la API no lo necesita para funcionar.**

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

Para comprobar que quedó bien declarado y conectado:

```bash
opencode mcp list
```

Debe listar `context7` como conectado. Ese comando es la forma documentada de verificar la
configuración; `opencode mcp add` escribe en la configuración global del equipo
(`~/.config/opencode/opencode.json`), no en la del proyecto.

> OpenCode 1.19.5 acepta también la forma anidada `mcp.servers.context7`. El proyecto usa la forma
> `mcp.context7` porque es la del esquema vigente.

## Estructura

| Ruta | Contenido |
|---|---|
| `docs/discovery/` | Informe de Discovery (secciones A–D y verificación de fuentes) |
| `knowledge-base/` | Los 10 archivos canónicos del producto |
| `CHANGES.md` | Roadmap, dependencias y camino crítico |
| `AGENTS.md`, `CLAUDE.md` | Reglas para el agente de IA |
| `openspec/specs/` | Especificaciones vigentes |
| `openspec/changes/archive/` | Changes cerrados (proposal, design, tasks, specs) |
| `openspec/specs/appointment-api/spec.md` | Especificación vigente de la API de turnos (sincronizada al archivar C-10) |
| `src/appointments.py` | Servicio de dominio de turnos (SQLite) |
| `src/api/` | Capa HTTP de la API de turnos |
| `tests/` | Un test o más por cada escenario del spec |
| `scripts/seed_demo_data.py` | Script de datos ficticios de demostración |
| `requirements.txt` | Dependencias fijadas de la API (FastAPI, Uvicorn, cliente de pruebas, framework de pruebas) |
| `opencode.json` | Configuración del proyecto: servidor MCP Context7, sin credenciales |
| `.opencode/skills/api-turnos/` | Skill propia del proyecto para trabajar en la API de turnos |
| `TPI/` | Documentación de entrega del TPI |

## Levantar la API

<!-- comando-de-arranque: inicio -->

```bash
.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

<!-- comando-de-arranque: fin -->

La API queda disponible solo en loopback:

| Recurso | URL |
|---|---|
| Documentación interactiva (Swagger) | `http://127.0.0.1:8000/docs` |
| Esquema OpenAPI | `http://127.0.0.1:8000/openapi.json` |

El puerto se puede cambiar en el comando; para que la prueba de arranque
(`tests/test_api_startup.py`) no choque con una demostración manual, usa uno
libre.

La base de datos se toma de la variable de entorno `APPOINTMENTS_DB_PATH`. Sin
esa variable, la API usa `data/demo.sqlite3`, la base de demostración con datos
ficticios.

### Operaciones expuestas

| Método | Ruta | Qué hace |
|---|---|---|
| `POST` | `/clinics/{clinic_id}/appointments` | Crea un turno |
| `GET` | `/clinics/{clinic_id}/appointments/{appointment_id}` | Consulta un turno |
| `PATCH` | `/clinics/{clinic_id}/appointments/{appointment_id}` | Reprograma el intervalo de un turno |
| `POST` | `/clinics/{clinic_id}/appointments/{appointment_id}/cancel` | Cancela un turno y libera sus recursos |
| `GET` | `/clinics/{clinic_id}/availability` | Consulta si un intervalo está libre, sin crear nada |

No hay listado de turnos, ni altas de recursos, ni autenticación. La consulta de disponibilidad no es un
listado: no devuelve turnos, sino si la franja está libre y qué recurso la ocupa.

### Consultar la disponibilidad de una franja

```bash
curl "http://127.0.0.1:8000/clinics/demo-clinic/availability?start_at=2026-12-01T09:00:00-03:00&end_at=2026-12-01T09:30:00-03:00&professional_id=demo-profesional&chair_id=demo-sillon"
```

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

`start_at`, `end_at` y `professional_id` son obligatorios; `chair_id` es opcional, pero **obligatorio** en
consultorios que administran sillones (si no, responde `422 chair_required`). Cuando la franja está ocupada,
la respuesta sigue siendo `200` con `available: false` y `conflicting_resource` en `"professional"` o `"chair"`:
un conflicto es el resultado de la consulta, no un error.

La consulta es orientativa: entre el `GET` y el alta otro turno puede ocupar la franja. El alta sigue siendo la
que valida, y sigue respondiendo `409` si encuentra un conflicto.

## Datos de demostración

La API no crea consultorios, profesionales, sillones, pacientes ni servicios: eso está
excluido del alcance. El script de demostración los prepara con identificadores
conocidos y **datos ficticios**.

```bash
.venv\Scripts\python.exe scripts\seed_demo_data.py
```

Identificadores que quedan disponibles para usar en Swagger:

| Recurso | Identificador |
|---|---|
| Consultorio | `demo-clinic` |
| Profesional | `demo-profesional` |
| Sillón | `demo-sillon` |
| Paciente | `demo-paciente` |
| Servicio | `demo-consulta` |

El script **no borra ni sobrescribe**: si un registro ya existe, lo deja como está y
lo informa. Podés ejecutarlo antes de cada demostración sin perder las reservas que
ya creaste. Para preparar otra base:

```bash
.venv\Scripts\python.exe scripts\seed_demo_data.py --database data/otra-base.sqlite3
```

Por defecto, script y API usan la misma base: `data/demo.sqlite3`. La API puede
apuntar a otra con la variable de entorno `APPOINTMENTS_DB_PATH`:

```bash
set APPOINTMENTS_DB_PATH=data/otra-base.sqlite3
```

> Las bases de datos **no se versionan**: `.gitignore` cubre `*.db` y `*.sqlite3`, así que la base de
> demostración nunca entra al repositorio. Solo hay que regenerarla con el script.

> En el prototipo, un paciente es solo un identificador opaco: el esquema no tiene
> ninguna columna para nombres, documentos, teléfonos o correos. Por eso los datos de
> demostración no pueden contener información personal real.

## Datos y privacidad

Todos los ejemplos, pruebas y capturas usan datos ficticios. No se almacenan datos reales de pacientes ni credenciales en este repositorio.
