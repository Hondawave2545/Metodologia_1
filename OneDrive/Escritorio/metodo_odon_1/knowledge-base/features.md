# Funcionalidades y alcance

**Estado:** backlog candidato; los elementos del MVP requieren validación en la fase 0 de `CHANGES.md`.

## MVP candidato — prioridad 0

| ID | Funcionalidad | Criterios de aceptación resumidos | Estado |
|---|---|---|---|
| MVP-01 | Configurar consultorio y zona horaria | El administrador puede crear/configurar el consultorio y su zona horaria; las vistas de agenda usan dicha zona. | Pendiente |
| MVP-02 | Usuarios y roles básicos | Titular, recepción y profesional ven y modifican solo las funciones permitidas para su rol y consultorio. | Pendiente |
| MVP-03 | Profesionales y servicios | El consultorio puede administrar profesionales, servicios y duración de cada servicio. | Pendiente |
| MVP-04 | Disponibilidad | Se pueden definir horarios por profesional y bloquear excepciones de agenda sin crear turnos ficticios. | Pendiente |
| MVP-05 | Gestión de pacientes mínima | Recepción puede registrar y actualizar datos mínimos de contacto; la pantalla no solicita historia clínica. | Pendiente |
| MVP-06 | Agenda y turnos | Se puede consultar agenda por profesional, crear, confirmar, reprogramar y cancelar turnos y marcar su resultado. | Pendiente |
| MVP-07 | Prevención de conflictos | Dos operaciones concurrentes no pueden reservar turnos superpuestos para el mismo profesional ni para el mismo sillón cuando el consultorio los administra; se permiten turnos adyacentes. | Prototipo SQLite implementado; validar e integrar antes del piloto |
| MVP-08 | Confirmaciones y recordatorios | El sistema puede enviar mensajes por WhatsApp mediante proveedor elegido, con consentimiento, registro de entrega y fallo visible. Su viabilidad es una puerta de decisión previa al piloto. | Pendiente |
| MVP-09 | Auditoría operativa | Los cambios relevantes guardan actor y fecha, sin replicar información sensible innecesaria. | Pendiente |

## Criterios transversales

- Interfaz en español y formatos de fecha/hora coherentes con la zona horaria del consultorio.
- Separación de datos entre consultorios y validación del permiso en el servidor.
- Errores de validación y fallos de notificación explícitos, sin aparentar éxito.
- Pruebas para permisos, conflictos de agenda, cambios de estado y conversión de horarios.
- No operar con datos reales hasta definir autenticación, copias de seguridad, monitoreo, respuesta a incidentes y revisión de privacidad.

## Fuera del MVP candidato

- Historia clínica completa, odontograma, periodontograma, imágenes clínicas, recetas y firma de consentimientos.
- Facturación electrónica, cobros, conciliación, liquidaciones de obras sociales, inventario y pagos en línea.
- Portal de autogestión, marketplace, videoconsultas, campañas y chatbot/recepcionista con IA.
- Integraciones no confirmadas con obras sociales, sistemas fiscales, calendarios externos o pasarelas de pago.

Repriorizar solo con evidencia de usuarios y una decisión de producto registrada. Las exclusiones no impiden reevaluarlas después del piloto.
