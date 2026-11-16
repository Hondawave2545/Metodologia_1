# Guion del video — TPI Metodología I

Duración total: **hasta 10 minutos** por equipo. Incluye explicación de changes, skill, MCP y demostración.
Todos los integrantes deben presentarse y hablar; cámara encendida al menos durante la presentación personal.

> Esquema base: distribución sugerida por la consigna. Es la estructura y el control de tiempos.
>
> **Estado de preparación (2026-11-16):** hay **3 changes completos y archivados** (C-05, C-10 y C-11), la
> **skill propia** y el **MCP Context7** están implementados, referenciados y con evidencia de uso real. La API
> tiene **cinco operaciones** verificadas por HTTP contra el servidor real. Todo el material que hay que mostrar
> está en el repositorio. **Lo único que falta es grabar.**
>
> Evidencia para este guion: `TPI/evidencia-skill-mcp.md` (skill y MCP) y `TPI/evidencia-verificacion-api.md`
> (secuencias reales por HTTP).

---

## 0:00–0:30 — Presentación del equipo y alcance alcanzado

| Tiempo | Contenido | Quién |
|---|---|---|
| 0:00–0:10 | Presentación: nombre y apellido de cada integrante, comisión. | Todos |
| 0:10–0:20 | Qué es el sistema: gestión de turnos y agenda para consultorios odontológicos. Recordar que el TPI **continúa el Parcial 2 sobre el mismo repositorio**. | ____________ |
| 0:20–0:30 | Alcance alcanzado en el TPI y qué queda pendiente. Decirlo de entrada, sin adornos. | ____________ |

**Puntos a cubrir**
- El proyecto no nació en el TPI: se conservan Discovery, `knowledge-base/`, `CHANGES.md`, `AGENTS.md` y los
  changes archivados del Parcial 2.
- Alcance real del TPI: **3 changes completos y archivados** (C-05, C-10, C-11), con **87 pruebas en verde**.
- Pendientes declarados: **autenticación y roles, frontend, altas de recursos por API, listados y
  persistencia de producción**; y en el roadmap los changes **C-01 a C-04** y **C-06 a C-09**.

---

## 0:30–3:00 — Recorrido por los changes completos: propósito, resultado y verificación

Mostrar el roadmap y el archivado de OpenSpec.

| Tiempo | Contenido | Quién |
|---|---|---|
| 0:30–0:45 | Abrir `CHANGES.md` y `openspec/changes/archive/`: mostrar la tabla del roadmap y las **3 carpetas archivadas**. | ____________ |
| 0:45–1:25 | **Change 1 (C-05 — crear turno sin solapamientos):** qué problema resuelve, qué generó, cómo se comprobó. | ____________ |
| 1:25–2:05 | **Change 2 (C-10 — agenda y turnos, API local con Swagger):** propósito, alcance, resultado y verificación. | ____________ |
| 2:05–2:40 | **Change 3 (C-11 — consulta de disponibilidad de un intervalo):** por qué hace falta (agendar sin crear a ciegas) y cómo se resolvió reutilizando la regla que ya existía. | ____________ |
| 2:40–3:00 | Trazabilidad: del spec al código y a las pruebas. Mencionar las dos specs vigentes. | ____________ |

**Para cada change completo, responder en palabras propias:**
1. ¿Qué problema resuelve?
2. ¿Qué generó o modificó?
3. ¿Cómo comprobaron el resultado?

**Artefactos a tener abiertos en pantalla**
- `CHANGES.md` (tabla de changes).
- `openspec/changes/archive/2026-10-15-crear-turno-sin-solapamientos/` (C-05).
- `openspec/changes/archive/2026-11-16-c10-api-turnos-swagger/` (C-10).
- `openspec/changes/archive/2026-11-16-c11-disponibilidad-intervalo/` (C-11).
- `openspec/specs/agenda-turnos/spec.md` (dominio) y `openspec/specs/appointment-api/spec.md` (API, 9 requisitos).

**Pendientes — mencionarlos explícitamente** (la consigna exige distinguirlos de lo terminado): C-01 a C-04,
C-06, C-07, C-08, C-09; autenticación y roles, frontend, altas por API, listados y persistencia de producción.
Decir que no se cuentan como funcionalidad completa.

---

## 3:00–6:00 — Skill propia y MCP: creación o conexión, integración y aplicación concreta

| Tiempo | Contenido | Quién |
|---|---|---|
| 3:00–3:40 | **Skill propia:** qué necesidad resuelve, qué skill creadora se usó, cómo la adaptaron, dónde quedó integrada y cómo se referencia desde `AGENTS.md`. | ____________ |
| 3:40–4:20 | **MCP:** cuál se conectó, qué capacidades aporta, cómo se comprobó la conexión, dónde está la configuración y por qué no hay credenciales en el repositorio. | ____________ |
| 4:20–5:20 | **Aplicación concreta:** en qué change se usaron, qué se pidió, qué resultado dio y cómo se revisó ese resultado. Mostrar la evidencia real. | ____________ |
| 5:20–6:00 | Qué aporta cada uno por separado (son incorporaciones distintas) y qué queda pendiente de cada una. | ____________ |

**Qué tiene que verse en pantalla (evidencia concreta, no una lista de nombres)**
- La skill: `.opencode/skills/api-turnos/SKILL.md` y sus dos referencias
  (`references/gotchas.md`, `references/contrato-http.md`), y su referencia en `AGENTS.md` y en
  `.atl/skill-registry.md`.
- La configuración del MCP: **`opencode.json`** en la raíz del proyecto (servidor remoto
  `https://mcp.context7.com/mcp`, **sin claves ni tokens**), y la comprobación con `opencode mcp list`.
- La solicitud textual, la salida obtenida y el cambio que produjo: `TPI/evidencia-skill-mcp.md` §3 y §4.

**Punto de la consigna a no olvidar:** *"Tener la skill y el MCP instalados o mostrar sus nombres en una lista
no demuestra su aplicación."* Hay que mostrar el **uso**, no la instalación. Para eso sirven las dos consultas
reales ya registradas:

1. **FastAPI, handlers de excepción** (C-10): la documentación oficial muestra que el handler por defecto de
   `RequestValidationError` devuelve `exc.body` en la respuesta. El proyecto deliberadamente devuelve un cuerpo
   controlado, para que un body con datos del paciente no se refleje en el error.
2. **FastAPI, parámetros de consulta** (C-11): la documentación muestra que los obligatorios se declaran sin
   default y el opcional con `default=None`, y que la descripción aparece en el esquema OpenAPI. Eso fijó cómo
   se declara la consulta de disponibilidad.

**Qué aporta cada una (5:20–6:00)**
- La **skill** deja el contrato, las trampas y el ciclo de trabajo del proyecto en un lugar que cualquier agente
  pueda aplicar; se nota en que la implementación de C-11 **no** reimplementó la regla de solapamiento: extrajo
  el helper que ya usaba el alta y lo reutilizó.
- El **MCP** aportó documentación oficial vigente en el momento de decidir, no de memoria.

---

## 6:00–10:00 — Resultado de las pruebas y demostración del sistema funcionando

El sistema debe estar **levantado y funcionando** antes de grabar. Preparar entorno y datos de prueba con
antelación.

| Tiempo | Contenido | Quién |
|---|---|---|
| 6:00–6:40 | Ejecutar la suite y mostrar el resultado en pantalla: `python -m unittest discover -s tests -v` (o `python -m pytest tests -v`). | ____________ |
| 6:40–8:00 | **Demostración de la API:** Swagger abierto en `/docs`, esquema en `/openapi.json`, y las **cinco operaciones** reales: crear, consultar, reprogramar, cancelar y **consultar la disponibilidad** de una franja. | ____________ |
| 8:00–9:00 | **Demostración del comportamiento clave:** caso de conflicto que devuelve `409` y no revela datos del paciente; intervalo inválido (`422`); aislamiento por consultorio; y la disponibilidad que dice qué recurso está ocupado. | ____________ |
| 9:00–9:40 | Relación entre lo demostrado y los escenarios verificables de los specs. | ____________ |
| 9:40–10:00 | Cierre: qué se logró, qué queda pendiente y a qué apunta el roadmap. | Todos |

**Qué tiene que verse**
- La salida de la suite (**87 passed**), resultado real, no una captura vieja.
- El backend en ejecución y Swagger respondiendo.
- Respuestas reales de los endpoints y **qué confirman** cada una.
- La salida del script de datos ficticios con los IDs documentados (`demo-clinic`, `demo-profesional`,
  `demo-sillon`, `demo-paciente`, `demo-consulta`).

**Las cinco operaciones, con su respuesta esperada**

| # | Operación | Resultado |
|---|---|---|
| 1 | `POST /clinics/{clinic_id}/appointments` | `201` con el turno creado, estado `scheduled` |
| 2 | `GET /clinics/{clinic_id}/appointments/{id}` | `200` con el turno |
| 3 | `PATCH /clinics/{clinic_id}/appointments/{id}` | `200` con el intervalo nuevo |
| 4 | `POST /clinics/{clinic_id}/appointments/{id}/cancel` | `200` con el turno ya `cancelled` (no es `204` ni `DELETE`) |
| 5 | `GET /clinics/{clinic_id}/availability` | `200` con `available` y `conflicting_resource` |

**Casos de error para mostrar**

| Caso | Resultado |
|---|---|
| Mismo profesional y franja ocupada | `409` `appointment_conflict` con `resource: professional` — **sin datos del paciente** |
| Intervalo inválido | `422` `invalid_appointment_interval` |
| Turno inexistente | `404` `appointment_not_found` |
| Profesional de otro consultorio | `422` `resource_unavailable` |

**Reglas de la consigna para la demo**
- Una API que nunca se ejecutó no acredita la funcionalidad: ejecutarla en video.
- No hace falta correr toda la suite en video: mostrar el resultado de los tests y las operaciones representativas.
- Frontend, si no existe, no se simula ni se presenta como integrado.

---

## Checklist técnico antes de grabar

- [ ] Suite verde en la máquina de grabación, con el comando exacto que se va a mostrar
      (`.venv\Scripts\python.exe -m pytest tests -v` → **87 passed**).
- [ ] API levantada en loopback (`127.0.0.1`) y `/docs` y `/openapi.json` respondiendo.
- [ ] Base de datos de demo creada con datos **ficticios** e IDs conocidos
      (`.venv\Scripts\python.exe scripts\seed_demo_data.py`).
- [ ] Pantallas y terminal con tamaño de fuente legible.
- [ ] Sin datos reales de pacientes, sin tokens ni contraseñas en pantalla ni en el repositorio.
- [ ] Cronómetro: sumar los cuatro bloques y no pasar de 10:00.
- [ ] Cada integrante tiene asignado un bloque de exposición.
- [ ] A la vista, listo para mostrar: `CHANGES.md`, la carpeta `openspec/changes/archive/`, el `README.md`,
      la skill, `opencode.json` y las dos evidencias de `TPI/`.

---

## Resumen de tiempos

| Bloque | Rango | Duración |
|---|---|---|
| Presentación del equipo y alcance | 0:00–0:30 | 0:30 |
| Changes completos (C-05, C-10, C-11) | 0:30–3:00 | 2:30 |
| Skill propia y MCP | 3:00–6:00 | 3:00 |
| Tests y demostración | 6:00–10:00 | 4:00 |
| **Total** | | **10:00** |
