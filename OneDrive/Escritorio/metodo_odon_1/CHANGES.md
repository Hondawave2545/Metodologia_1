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

> Nota: el prototipo de C-05 se adelantó a C-01–C-04 para validar la regla de negocio más crítica. Esos recursos (consultorio, profesional, sillón, paciente, servicio) existen hoy solo como tablas del prototipo SQLite, sin API ni autenticación.

## Fases

| Fase | Entregables | Criterio de salida | Estado |
|---|---|---|---|
| 0. Validar producto | Recomendación de la sección D (redactada); entrevistar consultorios; confirmar usuario objetivo, flujo prioritario, relevancia de sillones y disposición a pagar. | MVP aprobado por la responsable del producto con necesidades respaldadas por entrevistas. | Parcial: sección D redactada, entrevistas pendientes |
| 1. Definir experiencia y arquitectura | Flujos de agenda y pacientes, permisos, prototipo, decisiones de datos, privacidad, zona horaria y proveedor de mensajería. | Decisiones documentadas en `knowledge-base/decisiones.md` y `arquitectura.md`; costo de WhatsApp evaluado. | Pendiente |
| 2. Construir núcleo de agenda | C-01 a C-07: consultorio, roles, profesionales, servicios, **sillones**, horarios, pacientes, turnos, estados y validaciones de solapamiento. | Flujos esenciales probados de extremo a extremo con datos de prueba y aislamiento de acceso verificado. | En curso (C-05 archivado) |
| 3. Incorporar notificaciones | C-08: confirmaciones y recordatorios por WhatsApp, registro de entrega y fallos visibles. | Pruebas con consentimiento y entorno de prueba; fallos de envío detectables y recuperables. | Pendiente |
| 4. Pilotear y decidir expansión | C-09: piloto con consultorios, medición de adopción, errores y ausencias. | Decisión explícita: continuar, ajustar o detener. | Pendiente |

## Camino crítico

`C-01 → C-02 → C-04 → C-05 → C-06 → C-08 → C-09`

C-03 y C-07 pueden avanzar en paralelo una vez que existen sus dependencias, pero C-08 no puede empezar sin los estados de C-06.

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
