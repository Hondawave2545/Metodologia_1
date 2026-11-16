# Design

## Context

El repositorio tiene un único change implementado y archivado (C-05): `src/appointments.py`, un servicio de dominio sobre SQLite con control de solapamientos por profesional y sillón, verificado por 18 pruebas en `tests/test_appointments.py`. No existe capa HTTP, ni manifiesto de dependencias, ni configuración de agente del proyecto.

C-10 agrega una frontera HTTP sobre ese servicio para poder demostrarlo. La frontera debe ser verificable de punta a punta y no puede alterar la semántica de agenda fijada en `openspec/specs/agenda-turnos/spec.md`.

El equipo trabaja con **OpenCode** (no con VS Code). Esto condiciona dónde viven la configuración del servidor MCP y la skill propia: la documentación oficial de OpenCode (`opencode.ai/docs/mcp`, `opencode.ai/docs/skills`) define rutas distintas de las que asumía la primera versión de la propuesta.

Verificaciones previas realizadas sobre la instalación local (OpenCode 1.19.5, Python 3.14.8):

| Verificación | Resultado |
|---|---|
| Formato de config MCP `mcp.<nombre>` en `opencode.json` | Aceptado y conectado (`opencode mcp list` lo lista). Es la forma del esquema v1 y la que usa el proyecto |
| Formato de config MCP `mcp.servers.<nombre>` en `opencode.json` | Aceptado y conectado en 1.19.5 (verificado el 2026-11-16 con un servidor de prueba que solo existía en el archivo del proyecto). No es la forma del esquema v1, que declara los servidores directamente bajo `mcp` |
| `opencode mcp add` en 1.19.5 | Escribe en `~/.config/opencode/opencode.json`; **no** escribe en el proyecto (no tiene flag `--global` en esta versión) |
| Skill de proyecto en `.opencode/skills/<id>/SKILL.md` | Descubierta (`opencode debug skill` la lista; el id sale de la ruta) |
| Instalación de FastAPI + Uvicorn + httpx2 + pytest en Python 3.14.8 | Correcta: fastapi 0.162.7, uvicorn 0.54.0, starlette 1.10.0, pydantic 2.14.3, httpx2 2.16.0, pytest 9.2.0 (cliente de pruebas `httpx2`, ver D8) |
| Arranque con Uvicorn en `127.0.0.1` | `/docs` → 200 y `/openapi.json` → 200 |

## Goals / Non-Goals

**Goals:**

- Exponer por HTTP las cuatro operaciones que el dominio ya soporta, sin reimplementar regla de negocio.
- Que el contrato de la API sea autodescriptivo y verificable automáticamente.
- Que la skill propia y el servidor MCP queden integrados, referenciados y con evidencia de uso real.
- Que el repositorio permita reproducir el alcance: instalar, preparar datos ficticios, arrancar y probar.

**Non-Goals:**

- Cualquier forma de autenticación, autorización por rol o multiusuario.
- Altas de consultorios, profesionales, sillones, pacientes o servicios por la API.
- Listado de turnos, paginación, filtros, búsqueda o reportes.
- Cambios al dominio, a la semántica de intervalos `[inicio, fin)` o a los estados que bloquean recursos.
- Persistencia de producción: la persistencia sigue siendo SQLite local.
- Interfaz web de ningún tipo.

## Decisions

### D1. La configuración MCP del proyecto vive en `opencode.json`, no en `.vscode/mcp.json`

**Qué:** el servidor Context7 se declara en `opencode.json` en la raíz del repositorio, bajo `mcp.context7`, con `type: "remote"` y `url: "https://mcp.context7.com/mcp"`, sin cabeceras ni credenciales.

**Por qué:** el equipo usa OpenCode, y OpenCode no lee `.vscode/mcp.json`. La ruta oficial para la configuración compartida de proyecto es `opencode.json` (o `.opencode/opencode.json`) en la raíz. Además, `opencode.json` no está cubierto por `.gitignore`, así que el archivo queda versionado sin tener que habilitar excepciones, y quien clone el repositorio hereda la conexión MCP reproducible.

**Alternativas consideradas:**

- `.vscode/mcp.json`: es el formato de otro cliente; OpenCode lo ignoraría y quedaría una configuración muerta en el repositorio. Descartada.
- Solo configuración global (`~/.config/opencode/opencode.json`): no queda en el repositorio, no es reproducible al clonar y no sirve como evidencia del TPI. Descartada como configuración del proyecto; se mantiene como la configuración personal ya existente.
- Forma anidada `mcp.servers.<nombre>`: también registra y conecta el servidor en 1.19.5 (verificado el 2026-11-16 con un servidor de prueba que solo existía en el `opencode.json` del proyecto), pero no es la forma del esquema v1, que declara los servidores directamente bajo `mcp`. Se elige la forma del esquema, que es la que muestra la documentación oficial vigente y la que ya está implementada en el archivo del proyecto.

### D2. La skill propia vive en `.opencode/skills/api-turnos/SKILL.md`

**Qué:** la skill se crea como un directorio con `SKILL.md` (frontmatter `name` + `description`) y, si hace falta, `references/` y `scripts/` al lado, siguiendo el formato de Agent Skills que usa OpenCode.

**Por qué:** es la ruta de skills de proyecto que documenta OpenCode y que la instalación local ya descubre. El id de la skill lo determina el nombre del directorio (`api-turnos`), por lo que conviene que sea kebab-case y coincida con lo que se referencia en `AGENTS.md`.

**Alternativas consideradas:**

- `.claude/skills/`: OpenCode lo lee por compatibilidad, pero no es la ruta nativa del proyecto y no la documenta la fuente oficial. Descartada.
- `.github/skills/` (la ruta que asumía la propuesta original, tomada del plugin `agent-customization` de Copilot CLI): es de otro ecosistema. Descartada.
- Un `.md` suelto en la raíz de skills: la documentación reserva la forma de directorio para el `SKILL.md` cuando la skill tiene archivos auxiliares. Descartada.

### D3. La skill se crea con la skill creadora `skill-creator`

**Qué:** la skill se genera invocando la skill global `skill-creator` (`~/.config/opencode/skills/skill-creator/SKILL.md`), que es la creadora de skills del propio OpenCode en esta máquina.

**Por qué:** la consigna del TPI exige nombrar la skill creadora utilizada, y `skill-creator` es la herramienta disponible y coherente con el ecosistema. Cubre el ciclo completo (propósito, borrador, casos de prueba, iteración) y además es la que permite dejar los casos de prueba en `evals/evals.json` como evidencia.

**Alternativas consideradas:**

- `agent-customization` (plugin de Copilot CLI): era lo que decía la primera versión de la propuesta, pero pertenece a otro ecosistema y no está instalada. Descartada.
- Escribir la skill a mano: no permite acreditar el uso de una skill creadora. Descartada.

### D4. La API consume `src/appointments.py` sin reescribirlo

**Qué:** el adaptador HTTP es delgado. Traduce request → llamada al repositorio y traduce las excepciones del dominio → respuestas HTTP. La lógica de solapamientos, aislamiento por consultorio y normalización de intervalos queda íntegramente en el dominio.

**Por qué:** C-05 está archivado y verificado; duplicar esa lógica en la capa HTTP produciría dos fuentes de verdad para la regla más crítica del producto y rompería la trazabilidad entre spec, implementación y pruebas. La especificación de `appointment-api` describe comportamiento observable, no implementación, así que un adaptador delgado la satisface.

**Alternativas consideradas:**

- Reescribir el dominio dentro de la API: descartada por la duplicación de reglas y por perder la cobertura de las 18 pruebas existentes.
- Migrar a otro motor de persistencia: fuera de alcance; la decisión de persistencia de producción sigue abierta en el roadmap.

### D5. Mapeo explícito de errores de dominio a códigos HTTP

**Qué — códigos de éxito:**

| Operación | Respuesta | Cuerpo |
|---|---|---|
| Crear un turno | `201 Created` | El turno creado, con estado `scheduled` |
| Consultar un turno | `200 OK` | El turno consultado |
| Reprogramar un turno | `200 OK` | El turno con el intervalo nuevo |
| Cancelar un turno | `200 OK` | El turno ya cancelado, con estado `cancelled` |

La cancelación **no** responde `204` ni usa `DELETE`: el registro se conserva y el cliente
recibe el estado nuevo en la misma respuesta, sin una segunda consulta.

**Qué — errores:**

| Error del dominio | Respuesta HTTP |
|---|---|
| Conflicto de profesional o sillón | `409 Conflict` |
| Intervalo inválido (inicio ≥ fin, o sin zona horaria) | `422 Unprocessable Entity` |
| Recurso ausente, inactivo o ajeno al consultorio | `422 Unprocessable Entity` |
| Turno inexistente en el consultorio | `404 Not Found` |
| Turno no activo para reprogramar | `422 Unprocessable Entity` |
| Consultorio que administra sillones y la consulta no indica sillón | `422 Unprocessable Entity` |

El cuerpo del error expone un código estable y el recurso en conflicto, nunca la identidad del paciente.

**Por qué:** la consigna y el spec exigen que un conflicto se distinga de un error de entrada y que el error no filtre datos del paciente. `409` para conflicto y `422` para validación separates casos que un `400` genérico mezclaría, y `404` (no `403`) para un turno ajeno evita confirmar que ese turno existe.

**Alternativas consideradas:**

- `400` para todo error de entrada: no distingue conflicto de validación. Descartada.
- `403` para un turno de otro consultorio: revelaría la existencia del turno. Descartada.

### D6. Forma de las rutas y los verbos

**Qué:**

- `POST /clinics/{clinic_id}/appointments` — crear
- `GET /clinics/{clinic_id}/appointments/{appointment_id}` — consultar
- `PATCH /clinics/{clinic_id}/appointments/{appointment_id}` — reprogramar (solo intervalo)
- `POST /clinics/{clinic_id}/appointments/{appointment_id}/cancel` — cancelar

**Por qué:** el consultorio va en la ruta y no en un parámetro de consulta porque toda operación está aislada por consultorio y así queda explícito en el contrato. Cancelar es un verbo propio y no `DELETE` porque el turno no se borra: queda registrado con estado `cancelled`, y el spec exige que el registro se conserve. `PATCH` porque solo cambia el intervalo.

**Alternativas consideradas:**

- `DELETE` para cancelar: contradice la conservación del registro. Descartada.
- `clinic_id` como query param: menos explícito y más propenso a forgetarse. Descartada.

### D7. Dos capas de prueba: cliente de prueba y arranque real

**Qué:**

1. Pruebas HTTP de las operaciones y del mapeo de errores, ejecutadas contra la aplicación en proceso mediante el cliente de prueba del framework.
2. Una prueba de arranque que lanza el comando documentado (`uvicorn ... --host 127.0.0.1 --port <libre>`), espera a que el proceso esté listo y comprueba que el documento de contrato y la interfaz de documentación responden y que el contrato describe las cuatro operaciones.

**Por qué:** la consigna pide explícitamente un test automatizado de arranque con el comando documentado; y una prueba que solo usa el cliente de prueba no detectaría un comando de arranque roto (imports, módulo de la app, puerto). Son capas complementarias, no redundantes.

**Alternativas consideradas:**

- Solo cliente de prueba: más rápido, pero no prueba el comando de arranque. Descartada.
- Solo prueba de arranque: no cubre el detalle de los códigos de error. Descartada.

### D8. Dependencias de cliente de prueba y el aviso de deprecación observado

**Qué:** la verificación en Python 3.14 mostró que con starlette 1.10.0 el cliente de prueba emite `StarletteDeprecationWarning: Using 'httpx' with 'starlette.testclient' is deprecated; install 'httpx2' instead`. El manifiesto de dependencias debe declarar el cliente que el framework soporte sin avisos, fijando versiones que funcionen en Python 3.14.

**Por qué:** la suite debe correr limpia; un aviso de deprecación en cada ejecución es ruido que erosiona la señal de los resultados que se muestran en la demostración. La alternativa (`httpx` 0.28.1) funciona hoy, pero es el camino que el framework está dejando de soportar.

**Alternativas consideradas:**

- Fijar `httpx` y aceptar el aviso: funciona, pero deja una dependencia que el framework declara en desuso.
- Instalar `httpx2` (disponible, 2.16.0): es lo que el framework señala. Se prefiere, con verificación de que el cliente de prueba efectivamente lo usa.

### D9. Base de datos de demostración separada y script idempotente

**Qué:** la ruta de la base se toma de una variable de entorno con un valor por defecto; el script de datos de demostración prepara una base propia con identificadores conocidos y documentados (consultorio, profesional, sillón, paciente, servicio). El script crea lo que falta y **no** borra ni sobrescribe lo que ya existe.

**Por qué:** el proyecto ignora `*.db` y `*.sqlite3`, así que una base de demo nunca entra al repositorio. Mantener la demo separada evita tocar cualquier base de trabajo, y el comportamiento idempotente permite reejecutar el script antes de cada demostración sin romper nada.

**Alternativas consideradas:**

- Script que recrea la base desde cero: simple, pero destructivo y contrario a la regla de no pisar datos. Descartada.
- Sembrar la base desde la propia API: el alta de recursos por API está explícitamente excluida. Descartada.

### D10. Las incorporaciones del agente quedan dentro del repositorio y sin secretos

**Qué:** la skill, su configuración de descubrimiento y la entrada MCP quedan versionadas. La evidencia de uso se registra en `TPI/evidencia-skill-mcp.md` con la solicitud, la herramienta o procedimiento, el resultado y cómo se revisó.

**Por qué:** la consigna pide mantener en el repositorio "la skill, sus referencias y las instrucciones reproducibles del MCP, sin credenciales", y exige evidencia concreta de aplicación, no una lista de nombres instalados. El acceso a Context7 usa OAuth y las credenciales quedan fuera del repositorio.

**Alternativas consideradas:**

- Documentar solo en el README: la consigna pide un registro de evidencia con la estructura solicitud/resultado/revisión. Descartada.

## Risks / Trade-offs

- **[El cliente de prueba del framework pasa a preferir otro paquete HTTP]** → Se fija la dependencia que el framework declara soportada y se verifica que la suite corra sin avisos antes de archivar (ver D8).
- **[La versión de OpenCode instalada difiere de la documentación vigente]** → Se verificó en 1.19.5 que ambas formas (`mcp.<nombre>` y `mcp.servers.<nombre>`) registran el servidor y lo conectan; el proyecto usa la forma del esquema v1, que es la que muestra la documentación oficial vigente.
- **[`opencode mcp add` escribe en la configuración global, no en la del proyecto]** → El `opencode.json` del proyecto se edita a mano; el README documenta el comando de verificación (`opencode mcp list`) en lugar de un comando que no produce el resultado esperado.
- **[Acoplamiento con el dominio de C-05]** → Si cambia la firma del repositorio, la API rompe. Mitigación: el adaptador es delgado y las pruebas HTTP cubren la frontera; el cambio de dominio obliga a correr la suite completa.
- **[La API no tiene autenticación y cualquier proceso local puede llamarla]** → Riesgo aceptado y acotado: escucha solo en loopback, sin datos reales, y el README lo declara como no apto para operación clínica ni Internet.
- **[Un puerto ocupado hace fallar la prueba de arranque]** → La prueba de arranque elige un puerto libre al inicio y reintenta ante un conflicto acotado; nunca debe apuntar a un puerto fijo en paralelo con una demo manual.
- **[El MCP depende de un servicio externo con cupo mensual]** → No es requisito de ejecución ni de las pruebas: la suite debe pasar con el MCP desconectado, y esa condición es un escenario del spec.

## Migration Plan

No hay migración de datos: el cambio es aditivo y no modifica el dominio ni la base existente.

**Orden de despliegue local:**

1. Declarar las dependencias en el manifiesto Python e instalarlas en un entorno con Python 3.14.
2. Preparar la base de demostración ejecutando el script de datos ficticios.
3. Arrancar la API con el comando documentado, acotado a `127.0.0.1`.
4. Ejecutar la suite completa: dominio (18 pruebas) + API.

**Reversión:** eliminar el adaptador HTTP, el script de demostración y las entradas del manifiesto; el dominio de C-05 sigue funcionando sin cambios porque no se modifica `src/appointments.py`. La configuración MCP y la skill son archivos sueltos y se pueden retirar sin afectar la aplicación.

**Al archivar:** la especificación `appointment-api` se sincroniza en `openspec/specs/appointment-api/spec.md` y el estado de C-10 en `CHANGES.md` pasa a archivado, conservando la historia de los changes previos.

## Open Questions

Ninguna que afecte a las specs, al enfoque ni al desglose de tareas. Las decisiones que podrían haberlo hecho (motor HTTP, forma de las rutas, verbos, mapeo de errores, ubicación de la configuración MCP y de la skill, dependencia del cliente de prueba) quedaron resueltas en D1–D10.
