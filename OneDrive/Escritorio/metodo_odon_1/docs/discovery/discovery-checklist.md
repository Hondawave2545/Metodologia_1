# Checklist de Discovery (once puntos)

> **Borrador.** Resume lo investigado en `informe-discovery.md`. Si la skill `discovery-research` generó su propia salida estructurada, reemplazar o contrastar este archivo con esa salida y conservarla en esta carpeta.

| # | Punto | Resultado |
|:-:|:--|:--|
| 1 | **Problema** | Los consultorios coordinan agendas de varios profesionales con herramientas dispersas o manuales; hay conflictos de horario y trabajo manual de confirmación. Evidencia: solo documental. |
| 2 | **Usuarios** | Hipótesis: consultorios independientes o pequeños (uno a cinco profesionales), recepción y odontólogos; pacientes como destinatarios de confirmaciones. Sin validar. |
| 3 | **Casos de uso** | Crear, reprogramar, cancelar y confirmar turnos; evitar doble reserva de profesional y sillón; recordar al paciente; registrar el resultado del turno. |
| 4 | **Competidores** | 15 sistemas relevados (sección A); 7 puntuados. Principales: DentalSoft, ClinIA, AgendaPro, Nubimed, Dentalink, Dentidesk, Nimbo. |
| 5 | **Funcionalidades necesarias** | Agenda multiprofesional, reserva y recordatorios, estados de turno, roles, trazabilidad (estándar de mercado, sección C.1). |
| 6 | **Funcionalidades opcionales** | Odontograma e historia clínica, facturación ARCA, obras sociales, pagos, portal del paciente, chatbot, inventario, Google Calendar. |
| 7 | **Reglas de negocio** | Intervalos `[inicio, fin)`; solo `scheduled` y `confirmed` bloquean; sillón opcional por consultorio; aislamiento por consultorio; cancelar no borra. Ver `knowledge-base/reglas-de-negocio.md`. |
| 8 | **Integraciones** | WhatsApp (puerta de decisión), y a futuro ARCA, obras sociales, MercadoPago, Google Calendar. No confirmadas. |
| 9 | **Restricciones** | Datos de salud sensibles; sin datos reales de pacientes; WhatsApp con costo por mensaje y consentimiento; sin API ni autenticación todavía. |
| 10 | **Riesgos** | Diferenciación débil frente a DentalSoft y ClinIA; relevancia del sillón sin validar; exclusión de funciones clínicas; costo de mensajería; privacidad. |
| 11 | **Preguntas abiertas** | Ver `knowledge-base/preguntas-abiertas.md` (incluye todo lo "No evidenciado"). |
