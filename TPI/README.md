# TPI — Metodología I

Continuación del **Parcial 2** sobre el **mismo repositorio** (`metodo_odon_1`, sistema de turnos y agenda
de consultorios odontológicos). No es un proyecto nuevo: se conserva la fundación hecha con Active Stack
(Discovery, base de conocimiento, roadmap, instrucciones del agente) y el development con Spec-Driven
Development (OpenSpec).

- Consigna: `medotodlogiaconsigna_tpi.pdf`
- Roadmap vigente: `CHANGES.md`
- Base canónica del producto: `knowledge-base/`
- Reglas del agente: `AGENTS.md`, `CLAUDE.md`
- Artefactos SDD: `openspec/`

Este documento describe **el estado real verificado en el repositorio**, no la intención. Los changes solo se
marcan `completo` cuando están **archivados en OpenSpec y respaldados por pruebas ejecutadas**; los
elementos de entrega (skill propia, servidor MCP) se marcan `completo` cuando existen en el repositorio,
están referenciados y su configuración fue verificada con el comando que se indica en la evidencia.

## Estado verificado

Fecha de verificación: 2026-11-16. Verificación ejecutada sobre `openspec list`, `openspec status --change`,
el árbol de `openspec/changes/`, `src/`, `tests/` y la suite de pruebas local.

Última actualización (2026-11-16): se cerraron los grupos 6 (skill propia), 7 (MCP Context7) y **8**
(verificación integral y documentación) del change C-10; se corrigió la inconsistencia de documentación
detectada entre `proposal.md`, `design.md`, `spec.md`, `CHANGES.md` y el código, en dos puntos: la forma de la
clave MCP (`mcp.context7`) y el código de respuesta de la cancelación (`200`); **C-10 fue archivado** en
OpenSpec con su spec sincronizada; y se recorrió el ciclo SDD completo de un **segundo change, C-11**
(consulta de disponibilidad de un intervalo), que también quedó archivado.

Estado de la suite: **87 pruebas en verde el 2026-11-16**, ejecutadas con la configuración MCP del proyecto
apartada. Ninguna prueba depende del servidor MCP.

### Changes

| ID | Change | Estado | Evidencia / qué falta |
|---|---|---|---|
| C-01 | Configurar consultorio, zona horaria y roles | pendiente | Sin artefactos en `openspec/`. |
| C-02 | Profesionales, servicios y sillones | pendiente | Sin artefactos en `openspec/`. |
| C-03 | Disponibilidad y bloqueos de agenda | pendiente | Sin artefactos en `openspec/`. |
| C-04 | Pacientes con datos mínimos | pendiente | Sin artefactos en `openspec/`. |
| C-05 | Crear turno sin solapamientos (profesional y sillón) | **completo** | Archivado en `openspec/changes/archive/2026-10-15-crear-turno-sin-solapamientos/` (proposal, design, tasks, spec). Implementado en `src/appointments.py`, verificado en `tests/test_appointments.py`. Spec sincronizada en `openspec/specs/agenda-turnos/spec.md`. |
| C-06 | Estados del turno: confirmar, completar, ausente | pendiente | Sin artefactos en `openspec/`. |
| C-07 | Auditoría operativa (actor y fecha) | pendiente | Sin artefactos en `openspec/`. |
| C-08 | Confirmaciones y recordatorios por WhatsApp | pendiente | Sin artefactos en `openspec/`. Puerta de decisión. |
| C-09 | Piloto acotado y métricas | pendiente | Sin artefactos en `openspec/`. |
| C-10 | API local de turnos con Swagger | **completo** | **Archivado el 2026-11-16** en `openspec/changes/archive/2026-11-16-c10-api-turnos-swagger/` (proposal, design, tasks, spec). Implementación en `src/api/`, 42 pruebas, script de datos ficticios, skill propia y MCP con evidencia. Spec sincronizada en `openspec/specs/appointment-api/spec.md` (8 requisitos). Verificación: 60 pruebas en verde y secuencia real por HTTP reejecutada. |
| C-11 | Consulta de disponibilidad de un intervalo | **completo** | **Archivado el 2026-11-16** en `openspec/changes/archive/2026-11-16-c11-disponibilidad-intervalo/`. Quinta operación de la API (`GET /clinics/{clinic_id}/availability`): 27 pruebas nuevas (15 del dominio, 12 de la API) y secuencia real por HTTP registrada en `TPI/evidencia-verificacion-api.md` §0.1. Spec de `appointment-api` ampliada. |

### Skill propia, MCP, API y video

| Elemento | Estado | Evidencia / qué falta |
|---|---|---|
| Skill propia de workspace | **completo** | Existe en `.opencode/skills/api-turnos/SKILL.md` (frontmatter `name`/`description` con qué hace y cuándo se dispara, y el ciclo de trabajo en el cuerpo). Se completaron las dos referencias que la skill remite y que faltaban: `references/gotchas.md` y `references/contrato-http.md`. OpenCode la descubre: `opencode debug skill` → `"name": "API de turnos"`, `"location": "...\.opencode\skills\api-turnos\SKILL.md"` (identificador derivado de la ruta: `api-turnos`). Referenciada con la ruta exacta en `AGENTS.md` y en `CLAUDE.md` (sección `## Skills del proyecto`) y registrada en `.atl/skill-registry.md`. Tareas 6.1–6.4 verificadas. |
| Servidor MCP (Context7) | **completo** | Configurado **en el repositorio**: `opencode.json` en la raíz con `mcp.context7` (`type: remote`, `url: https://mcp.context7.com/mcp`, `enabled: true`), sin claves, tokens ni encabezados con credenciales. Verificado con `opencode mcp list` desde la raíz del proyecto → `✓ context7 connected`, y con `git check-ignore opencode.json` → exit 1 (no ignorado: se versiona). Para probar que la conexión viene del archivo del proyecto y no solo del global, se agregó un servidor temporal `context7-proyecto-temporal` existente únicamente en `opencode.json`: apareció en `opencode mcp list` (3 servidores) y se quitó después. Consulta real de documentación de FastAPI registrada en `TPI/evidencia-skill-mcp.md`. Tareas 7.1–7.5 verificadas. |
| API FastAPI + Swagger | completo | **Implementada, probada y archivada.** `src/api/` (app, esquemas, mapeo de errores, configuración). **Cinco** endpoints: crear, consultar, reprogramar, cancelar y consultar la disponibilidad de un intervalo. Swagger en `/docs` y OpenAPI en `/openapi.json`. Dependencias fijadas en `requirements.txt` y verificadas en Python 3.14.8. Secuencia real por HTTP reejecutada el 2026-11-16 contra uvicorn como proceso real (`curl.exe` sobre `127.0.0.1`): los 10 códigos esperados se cumplen y coinciden con lo registrado. |
| Video de presentación (10 min) | pendiente | No existe. Guion preparado en `TPI/guion-video.md`. |
| Archivo de entrega `.txt` | pendiente | Modelo preparado en `TPI/entrega-borrador.txt`, con campos sin completar. |

## Estado de las pruebas

Suite actual: 7 archivos. `tests/test_appointments.py` (dominio de C-05, sin modificar), cuatro archivos de
C-10 (`test_api_contract.py`, `test_api_operations.py`, `test_api_startup.py`, `test_seed_demo_data.py`) y dos
de C-11 (`test_availability_domain.py`, `test_api_availability.py`).

| Comando | Resultado verificado (2026-11-16, con la configuración MCP del proyecto apartada) |
|---|---|
| `.venv\Scripts\python.exe -m pytest tests -q` | `87 passed` |
| `.venv\Scripts\python.exe -m unittest discover -s tests` | `Ran 87 tests ... OK` |
| `.venv\Scripts\python.exe -m pytest tests -q -W error::DeprecationWarning` | `87 passed` (sin avisos) |

Además: `Select-String` de `mcp|context7|opencode` sobre `tests/`, `src/` y `scripts/` → **0 coincidencias**.
Ninguna prueba depende del servidor MCP; el escenario "La suite funciona sin el servidor MCP disponible"
del spec se cumple.

Python 3.14.8 · pytest 9.2.0 · fastapi 0.162.7 · uvicorn 0.54.0 · httpx2 2.16.0.

Cobertura:

- **Dominio (C-05):** 18 pruebas. No se modificaron ni `src/appointments.py` ni `tests/test_appointments.py`.
- **Contrato HTTP (C-10):** 15 pruebas del mapeo de errores (409 / 422 / 404) y de los esquemas. Incluye una
  prueba de fuga: el cuerpo del error no reproduce el texto de la excepción, por lo que no puede filtrar datos
  del paciente.
- **Operaciones (C-10):** 19 pruebas de las cuatro operaciones y de los casos límite: conflicto de profesional
  y de sillón, intervalo inválido, recurso ausente o inactivo, turno inexistente, aislamiento entre consultorios
  y sillón obligatorio.
- **Arranque (C-10):** 3 pruebas que lanzan el comando documentado del README en loopback y comprueban que
  `/docs` y `/openapi.json` responden y que el contrato expone exactamente las cinco operaciones, sin listado
  en la colección de turnos.
- **Datos ficticios (C-10):** 5 pruebas del script: crea los recursos con identificadores conocidos, es
  idempotente, no sobrescribe un consultorio preexistente y la base no tiene ninguna columna para datos personales.
- **Disponibilidad (C-11):** 27 pruebas (15 del dominio y 12 de la API): intervalo libre, conflicto de
  profesional y de sillón, turno cancelado que no bloquea, intervalo inválido o sin zona horaria, recurso
  ausente, inactivo o ajeno al consultorio, sillón obligatorio y no divulgación de datos del paciente.

## Archivos agregados en los grupos 6–7 (2026-11-16)

| Archivo | Qué es |
|---|---|
| `.opencode/skills/api-turnos/SKILL.md` | Skill propia del proyecto para trabajar en la API de turnos: qué leer, reglas no negociables, ciclo TDD, verificación y trampas. |
| `.opencode/skills/api-turnos/references/gotchas.md` | Trampas ya pagadas: cliente de pruebas `httpx2`, cierre de SQLite en Windows, constante de estado deprecada, prueba de arranque, orden de validación. |
| `.opencode/skills/api-turnos/references/contrato-http.md` | Referencia rápida del contrato: rutas, esquemas, códigos de éxito y error, mapeo desde los errores del dominio y datos de demostración. |
| `opencode.json` | Configuración del proyecto: Context7 como servidor MCP remoto, sin credenciales. |
| `tests/test_availability_domain.py` | Pruebas del dominio de la consulta de disponibilidad (C-11). |
| `tests/test_api_availability.py` | Pruebas HTTP de la consulta de disponibilidad (C-11). |

## Comandos para reproducir la demostración

```bash
# 1. Instalar dependencias (Python 3.14)
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Preparar los datos ficticios de demostración
.venv\Scripts\python.exe scripts\seed_demo_data.py

# 3. Levantar la API en loopback
.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000

# 4. Abrir Swagger en http://127.0.0.1:8000/docs
# 5. Ejecutar la suite
.venv\Scripts\python.exe -m pytest tests -v

# 6. Comprobar el MCP configurado en el proyecto (debe listar context7 conectado)
opencode mcp list
```

Identificadores de demostración: `demo-clinic`, `demo-profesional`, `demo-sillon`, `demo-paciente`, `demo-consulta`.

## Brecha contra el mínimo de la consigna

La consigna exige **2 changes válidos por integrante** (`mínimo total = 2 × cantidad de integrantes`), y un
change cuenta solo si recorrió el ciclo SDD completo: **propuesto → aplicado → verificado → archivado**.

Con **1 integrante** el mínimo es **2 changes válidos**. Hoy hay **3**: C-05, C-10 y C-11. **La brecha está
cerrada.**

| Change | Propósito | Estado | Verificación |
|---|---|---|---|
| C-05 | Crear turno sin solapamientos (profesional y sillón) | archivado (2026-10-15) | 18 pruebas del dominio, sin modificar |
| C-10 | Agenda y turnos: API local con Swagger sobre el dominio de C-05 | archivado (2026-11-16) | 42 pruebas de la API + secuencia real por HTTP |
| C-11 | Consulta de disponibilidad de un intervalo | archivado (2026-11-16) | 27 pruebas nuevas + secuencia real por HTTP |

Los tres recorrieron el ciclo completo: artefactos SDD, implementación, pruebas ejecutadas y archivado en
OpenSpec con su spec sincronizada.

Lo que queda pendiente **no es de código**: es la entrega.

| Pendiente | Qué falta |
|---|---|
| **Video de 10 minutos** | No existe. El guion está en `TPI/guion-video.md`; hay que grabarlo y subirlo a un enlace accesible. |
| **Archivo de entrega `.txt`** | El modelo está en `TPI/entrega-borrador.txt`, con el nombre y apellido del integrante sin completar. |
| **Enlace al repositorio** | Confirmar que el remoto `https://github.com/Hondawave2545/Metodologia_1` tiene los changes archivados que se presentan. |
| **Verificación de los enlaces** | Comprobar que el docente puede abrir el video y el repositorio sin pedir acceso. |

## Consistencia de la documentación (2026-11-16)

Se compararon `proposal.md`, `design.md`, `specs/appointment-api/spec.md`, `CHANGES.md`, `README.md`,
`TPI/` y el código en dos puntos. Correcciones aplicadas:

| Punto | Inconsistencia encontrada | Corrección |
|---|---|---|
| Forma de la clave MCP | `proposal.md`, `design.md`, `CHANGES.md` y `tasks.md` (tarea 7.1) decían `mcp.servers.context7`, pero `opencode.json` usa `mcp.context7` | Todo dice ahora `mcp.context7`. Se verificó además que **ambas** formas registran y conectan el servidor en OpenCode 1.19.5, y que la forma anidada queda documentada como alternativa aceptada. |
| Código de la cancelación | `proposal.md`, `design.md` (D5) y el código dicen `200`; el `spec.md` solo decía "respuesta exitosa" | El `spec.md` ahora fija `200` explícitamente y aclara que no debe responder `204` ni usar `DELETE`. El código nunca devuelve `204` (verificado: `204` no aparece en `src/api/`). |
| Bonus: fila obsoleta | `design.md` decía "httpx 0.28.1 instalado", pero D8 del mismo documento decide `httpx2` | La fila de la tabla de verificaciones dice `httpx2 2.16.0`, que es lo que el manifiesto fija y lo que la suite usa. |

Consecuencia: `openspec validate c10-api-turnos-swagger --strict` → `Change 'c10-api-turnos-swagger' is valid`.

## Nota sobre datos y secretos

Todos los ejemplos, pruebas, datos de demo y capturas usan **datos ficticios**. No se almacenan datos reales
de pacientes ni credenciales en el repositorio, en la entrega ni en el video.

## Contenido de esta carpeta

| Archivo | Qué es |
|---|---|
| `README.md` | Este documento: estado real verificado y brechas. |
| `evidencia-skill-mcp.md` | Evidencia **completa** de la skill propia y del MCP: solicitud textual, herramienta invocada, salida literal de Context7, tabla de revisión y checklist. |
| `evidencia-verificacion-api.md` | Secuencia real por HTTP contra uvicorn levantado como proceso real (crear 201, consultar 200, reprogramar 200, conflicto 409, intervalo inválido 422, inexistente 404, cancelar 200), con su reverificación del 2026-11-16. |
| `guion-video.md` | Esquema del video de 10 minutos según la distribución de la consigna. |
| `entrega-borrador.txt` | Modelo del archivo de entrega `.txt` con los campos pendientes marcados. |
