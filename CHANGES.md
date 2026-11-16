# Roadmap de implementación

Este roadmap define la secuencia de trabajo para un **MVP candidato** centrado en agenda y confiabilidad operativa. No es una aprobación del producto: el MVP sigue siendo una hipótesis que debe validarse con consultorios (Fase 0). Está alineado con la sección D de `docs/discovery/informe-discovery.md`.

## Alcance candidato del MVP (alineado con la sección D)

**Imprescindible (P0)**
- Configuración de consultorio, zona horaria, profesionales, servicios, horarios y roles básicos.
- Pacientes con datos mínimos de contacto (sin datos clínicos).
- Agenda por profesional; crear, confirmar, reprogramar y cancelar turnos; estados operativos.
- Prevención atómica de solapamientos por **profesional** y, en consultorios que los administran, por **sillón**; se permiten turnos consecutivos.
- Trazabilidad (actor y fecha) y permisos por rol.

**Diferenciador a validar (P1)**
- Confirmaciones y recordatorios por WhatsApp con consentimiento, estado de entrega y fallos visibles. Es una **puerta de decisión**: proveedor, costo (Meta cobra por mensaje) y consentimiento deben validarse antes del piloto.

**Fuera del primer MVP:** odontograma e historia clínica, facturación electrónica ARCA, obras sociales, pagos, portal del paciente, chatbot, inventario, integración con calendarios externos.

## Lista de changes

| ID | Change | Features | Depende de | Estado |
|---|---|---|---|---|
| C-01 | Configurar consultorio, zona horaria y roles | MVP-01, MVP-02 | — | Pendiente |
| C-02 | Profesionales, servicios y sillones | MVP-03 | C-01 | Pendiente |
| C-03 | Disponibilidad y bloqueos de agenda | MVP-04 | C-02 | Pendiente |
| C-04 | Pacientes con datos mínimos | MVP-05 | C-01 | Pendiente |
| C-05 | **Crear turno sin solapamientos (profesional y sillón)** | MVP-06, MVP-07 | C-02, C-04 | **Archivado** (prototipo SQLite, 2026-10-15) |
| C-06 | Estados del turno: confirmar, completar, ausente | MVP-06 | C-05 | Pendiente |
| C-07 | Auditoría operativa (actor y fecha) | MVP-09 | C-05 | Pendiente |
| C-08 | Confirmaciones y recordatorios por WhatsApp | MVP-08 | C-06 | Pendiente (puerta de decisión) |
| C-09 | Piloto acotado y métricas | — | C-08 | Pendiente |
| C-10 | **Agenda y turnos** (API local con Swagger sobre el dominio de C-05) | MVP-06, MVP-07 (expuestas por HTTP) | C-05 | **Archivado** (2026-11-16, `openspec/changes/archive/2026-11-16-c10-api-turnos-swagger/`) |
| C-11 | **Consulta de disponibilidad de un intervalo** (agendar sin crear a ciegas) | MVP-06 | C-05, C-10 | **Archivado** (2026-11-16, `openspec/changes/archive/2026-11-16-c11-disponibilidad-intervalo/`) |

> Nota: el prototipo de C-05 se adelantó a C-01–C-04 para validar la regla de negocio más crítica. Esos recursos (consultorio, profesional, sillón, paciente, servicio) existen hoy solo como tablas del prototipo SQLite, sin API ni autenticación.
>
> C-10 es una rama técnica de demostración que depende únicamente del servicio de C-05. No reemplaza ni cierra C-01–C-04 o C-06–C-09, no habilita uso con datos reales y no cambia la historia archivada de C-05.

## C-10 — Agenda y turnos (archivado)

**Propósito:** **Agenda y turnos**. Exponer por HTTP las operaciones de agenda ya implementadas en el dominio
(creación, consulta individual, reprogramación y cancelación), de modo que el producto de turnos tenga una
frontera consumible y demostrable: un cliente puede operar la agenda y leer su propio contrato.

**Dependencia real:** C-05. C-10 **no** implementa la regla de negocio: la toma del servicio de dominio ya
archivado (`src/appointments.py`, sin solapamientos por profesional y sillón) y agrega la capa HTTP encima.
Por eso C-10 no depende de C-01–C-04 ni de C-06–C-09, y no los reemplaza: no habilita autenticación, ni
altas de recursos, ni listados, ni persistencia de producción.

**Estado:** archivado el 2026-11-16 en `openspec/changes/archive/2026-11-16-c10-api-turnos-swagger/`
(proposal, design, tasks y spec). Especificación sincronizada en `openspec/specs/appointment-api/spec.md`
(8 requisitos). Verificado con 60 pruebas en verde y una secuencia real por HTTP registrada en
`TPI/evidencia-verificacion-api.md`.

**Alcance (entregado)**
- API FastAPI ejecutable con Uvicorn y documentación Swagger/OpenAPI. Rutas para crear, consultar por consultorio e ID, reprogramar y cancelar; no se agrega listado de turnos.
- Prueba automatizada de arranque con el comando documentado que consulta `/docs` y `/openapi.json`; pruebas HTTP para operaciones y mapeo explícito de errores del dominio.
- Verificar instalación de dependencias declaradas y ejecución de pruebas con Python 3.14.
- Script de datos ficticios para crear/verificar consultorio, profesional, sillón, paciente y servicio con IDs conocidos; documentar en README cómo iniciar la API y usar esos IDs desde Swagger.
- Skill propia de workspace para trabajar en la API de turnos, creada con la skill creadora `skill-creator` de OpenCode, ubicada en `.opencode/skills/api-turnos/SKILL.md` y referenciada en `AGENTS.md`; documentar qué creador se usó.
- Configuración compartida de Context7 MCP en `opencode.json` (raíz del repositorio), bajo `mcp.context7`, sin secretos. Ese archivo no está en `.gitignore`, así que queda versionado sin dejar de ignorar la configuración personal. Usarlo durante el cambio para consultar documentación vigente de FastAPI/Python; no es dependencia de ejecución ni de las pruebas.

**Rutas de OpenCode confirmadas (verificadas contra la documentación oficial y contra la instalación local, OpenCode 1.19.5):**

| Elemento | Ruta |
|---|---|
| MCP del proyecto | `opencode.json` en la raíz, clave `mcp.context7` |
| MCP global (equipo) | `~/.config/opencode/opencode.json` |
| Skill propia del proyecto | `.opencode/skills/<id>/SKILL.md` |
| Skill creadora | `~/.config/opencode/skills/skill-creator/SKILL.md` |

**Exclusiones:** autenticación, roles, altas por API de consultorios/recursos/pacientes/servicios, cambios al dominio o a la semántica de agenda, estados adicionales, auditoría, notificaciones y operación de producción. La API debe quedar limitada a loopback y a datos ficticios.

**Escenarios verificables (cumplidos y verificados)**
1. La prueba automatizada arranca el comando documentado en loopback y comprueba que Swagger y OpenAPI responden y describen las cuatro operaciones.
2. Crear devuelve el turno; consultarlo devuelve ese mismo turno dentro del consultorio indicado.
3. Reprogramar actualiza el intervalo; un conflicto o intervalo inválido devuelve un error explícito y no modifica la reserva original.
4. Cancelar conserva el registro, lo marca cancelado y libera profesional/sillón para una nueva reserva.
5. IDs inexistentes o de otro consultorio no filtran datos; los errores no contienen identidad del paciente en conflicto.
6. El script prepara los IDs ficticios documentados sin sobrescribir datos preexistentes; la suite y sus dependencias se verifican en Python 3.14.
7. La skill propia, creada con `skill-creator`, queda en `.opencode/skills/api-turnos/SKILL.md`, es descubierta por OpenCode y se referencia desde `AGENTS.md` para que el agente la use.
8. El agente puede resolver y consultar documentación pública de FastAPI mediante Context7 MCP desde la configuración del proyecto; las pruebas de la API siguen funcionando sin el MCP disponible.

> La consulta al MCP Context7 que fijó la forma de declarar el contrato (códigos de éxito y errores publicados
> en el documento OpenAPI) está registrada en el `proposal.md` archivado.

## C-11 — Consulta de disponibilidad de un intervalo

**Propósito:** que un cliente pueda **preguntar si una franja está libre antes de agendar**. Hoy el alta es a
ciegas: se envía el `POST` y el conflicto aparece después, como `409`. La disponibilidad es la consulta que
precede a toda reserva.

**Alcance**
- Una operación de solo lectura: `GET /clinics/{clinic_id}/availability`, con `start_at`, `end_at` y
  `professional_id` obligatorios y `chair_id` opcional.
- Respuesta `200` con `available` y `conflicting_resource` (`"professional"`, `"chair"` o nulo). Un conflicto
  es el **resultado** de la consulta, no un error: por eso esta operación no devuelve `409`.
- El solapamiento se resuelve en el dominio, con la **misma** detección de conflictos que usa el alta: no hay
  dos definiciones de la regla más crítica del producto.
- Errores con el mapeo ya existente: `422 invalid_appointment_interval`, `422 resource_unavailable`,
  `422 chair_required`.
- El contrato publica la operación y sus errores en el documento OpenAPI.

**Exclusiones:** no hay listado de turnos (la consulta no devuelve turnos), ni altas de recursos, ni
autenticación, ni paginación, ni horarios de atención, ni persistencia de producción. La consulta es
orientativa: entre el `GET` y el alta otro turno puede ocupar la franja, y el alta sigue validando.

**Dependencias:** C-05 (la regla de solapamiento del dominio) y C-10 (la capa HTTP, el contrato y las
convenciones). No depende de C-01–C-04 ni de C-06–C-09, y no los reemplaza.

**Escenarios verificables**
1. La consulta de un intervalo libre responde `200` con `available: true` y sin recurso en conflicto.
2. La consulta de un intervalo ocupado por el profesional responde `200` con `available: false` y
   `conflicting_resource: "professional"`, sin revelar datos del paciente.
3. La consulta de un intervalo ocupado por el sillón responde `200` con `conflicting_resource: "chair"`.
4. Un turno cancelado no bloquea: la consulta responde `available: true`.
5. Un intervalo inválido o sin zona horaria responde `422 invalid_appointment_interval`.
6. Un profesional ausente, inactivo o ajeno al consultorio responde `422 resource_unavailable`.
7. Un consultorio que administra sillones y la consulta sin `chair_id` responde `422 chair_required`.
8. La consulta no crea ni modifica ningún turno.

**Estado:** archivado el 2026-11-16 en `openspec/changes/archive/2026-11-16-c11-disponibilidad-intervalo/`
(proposal, design, tasks y spec). Verificado con 87 pruebas en verde y con una secuencia real por HTTP
registrada en `TPI/evidencia-verificacion-api.md` §0.1.

**MCP propuesto y evaluación (10-11-2026):** Context7 MCP, servidor alojado en `https://mcp.context7.com/mcp`. Expone `resolve-library-id` y `query-docs`, adecuados para buscar documentación de FastAPI sin otorgar acceso al filesystem ni permisos de escritura sobre el repositorio. La documentación publica un plan Free de **USD 0**, con 1.000 llamadas mensuales; al agotarse, las solicitudes se detienen hasta el próximo mes (con 20 llamadas extra por día). El plan Pro publicado es USD 10 por usuario/mes; no se propone ni requiere para este cambio. El acceso MCP usa OAuth; no incluir API keys en el repositorio. Referencias: [MCP en OpenCode](https://opencode.ai/docs/mcp/), [skills en OpenCode](https://opencode.ai/docs/skills/), [planes y precios de Context7](https://context7.com/docs/plans-pricing).

## Fases

| Fase | Entregables | Criterio de salida | Estado |
|---|---|---|---|
| 0. Validar producto | Recomendación de la sección D (redactada); entrevistar consultorios; confirmar usuario objetivo, flujo prioritario, relevancia de sillones y disposición a pagar. | MVP aprobado por la responsable del producto con necesidades respaldadas por entrevistas. | Parcial: sección D redactada, entrevistas pendientes |
| 1. Definir experiencia y arquitectura | Flujos de agenda y pacientes, permisos, prototipo, decisiones de datos, privacidad, zona horaria y proveedor de mensajería. | Decisiones documentadas en `knowledge-base/decisiones.md` y `arquitectura.md`; costo de WhatsApp evaluado. | Pendiente |
| 2. Construir núcleo de agenda | C-01 a C-07: consultorio, roles, profesionales, servicios, **sillones**, horarios, pacientes, turnos, estados y validaciones de solapamiento. C-10 es una rama técnica separada para exponer el prototipo C-05. | Flujos esenciales probados de extremo a extremo con datos de prueba y aislamiento de acceso verificado. | En curso (C-05 y C-10 archivados; C-01–C-04 y C-06–C-07 pendientes) |
| 3. Incorporar notificaciones | C-08: confirmaciones y recordatorios por WhatsApp, registro de entrega y fallos visibles. | Pruebas con consentimiento y entorno de prueba; fallos de envío detectables y recuperables. | Pendiente |
| 4. Pilotear y decidir expansión | C-09: piloto con consultorios, medición de adopción, errores y ausencias. | Decisión explícita: continuar, ajustar o detener. | Pendiente |

## Camino crítico

`C-01 → C-02 → C-04 → C-05 → C-06 → C-08 → C-09`

C-03 y C-07 pueden avanzar en paralelo una vez que existen sus dependencias, pero C-08 no puede empezar sin los estados de C-06.

La rama de demostración `C-05 → C-10` quedó **archivada** (C-05 en 2026-10-15, C-10 en 2026-11-16). Sigue
siendo una rama técnica: no altera las dependencias funcionales del camino crítico ni convierte el prototipo
en un MVP listo para piloto.

## Riesgos y dependencias

- **Producto:** el cliente objetivo (uno a cinco profesionales), el problema de coordinación y la relevancia del sillón son hipótesis; el Discovery es documental, no hay entrevistas.
- **Competitivo:** DentalSoft y ClinIA ya combinan agenda, WhatsApp y obras sociales con evidencia pública; competir solo con "agenda online + WhatsApp" no sería diferenciación (ver sección C).
- **Mensajería:** requiere verificar proveedor, costos por mensaje, consentimiento, entregabilidad y políticas vigentes antes del piloto.
- **Clínica mínima:** el MVP excluye odontograma; decidir antes del piloto si un odontograma básico es condición de adopción.
- **Datos personales:** la información de salud requiere revisión de privacidad, seguridad y obligaciones aplicables en Argentina antes de manejar datos reales.
- **Persistencia:** SQLite con `BEGIN IMMEDIATE` sirve para el prototipo; la persistencia de producción está sin decidir.

## Orden de dependencias

`Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4`

Una expansión funcional requiere resultados del piloto y una decisión de producto; no forma parte del compromiso de este roadmap.
