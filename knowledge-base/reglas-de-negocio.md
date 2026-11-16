# Reglas de negocio

**Estado:** reglas candidatas del MVP; revisar con usuarios y asesoramiento especializado donde corresponda.

## Agenda y turnos

1. Todo turno pertenece a un consultorio, profesional, paciente y servicio del mismo consultorio.
2. El fin del turno debe ser posterior al inicio. La duración se deriva del servicio o de un ajuste explícito permitido por el consultorio.
3. No se puede crear ni reprogramar un turno que se solape con otro turno activo (`scheduled` o `confirmed`) del mismo profesional ni, si el consultorio administra sillones, del mismo sillón. La validación debe ser atómica para evitar conflictos concurrentes.
4. Los turnos son intervalos semiabiertos `[inicio, fin)`: dos turnos consecutivos cuyos extremos coinciden no se solapan. El inicio debe ser anterior al fin.
5. La disponibilidad debe calcularse con la zona horaria del consultorio y considerar horarios y excepciones configurados. Los cambios de horario local deben mostrarse sin ambigüedad.
6. Crear, confirmar, reprogramar o cancelar un turno registra actor y fecha. La cancelación conserva el registro operativo; no se borra como si nunca hubiera existido.
7. Los estados operativos son `scheduled`, `confirmed`, `cancelled`, `completed` y `no_show`. Las transiciones permitidas deben ser explícitas; un turno cancelado no se reactiva silenciosamente: se crea o programa una nueva reserva. Solo los estados `scheduled` y `confirmed` bloquean recursos.
8. Reprogramar preserva la trazabilidad del turno original y valida de nuevo la disponibilidad, excluyendo el turno original de su propia búsqueda de conflictos.
9. La política de anticipación mínima, duración de bloques, tolerancia, lista de espera y ausencia de pacientes está pendiente de validación.

## Pacientes y acceso

10. Solo se solicitan datos personales necesarios para identificar y coordinar al paciente. Los duplicados se revisan sin fusionar registros automáticamente.
11. Toda lectura o modificación de datos debe comprobar la pertenencia y el rol dentro del consultorio dueño del registro.
12. No recopilar diagnósticos, tratamientos ni otra información clínica en la ficha de contacto del MVP candidato.
13. Las solicitudes de exportación, corrección o eliminación requieren un procedimiento y revisión de obligaciones aplicables antes del lanzamiento; no se debe prometer una política legal aún no definida.

## Mensajería

14. Enviar confirmaciones o recordatorios únicamente por un canal configurado por el consultorio y permitido para ese paciente.
15. Registrar canal, propósito, fecha, resultado de entrega y fallos de forma acotada. No registrar tokens, secretos ni contenido innecesario.
16. Un envío fallido no cambia el estado del turno ni se presenta como exitoso; debe ser visible para el operador.
17. Ventanas, frecuencia, horarios de silencio, consentimiento y proveedor de mensajería se deben validar antes del piloto.

## Auditoría y seguridad

18. Registrar de manera no ambigua quién realizó cambios relevantes de agenda, accesos administrativos y operaciones de mensajería.
19. No exponer datos de un consultorio a otro ni en búsquedas, exportaciones, notificaciones o registros.
20. Usar controles de acceso por rol, manejo seguro de credenciales, copias de seguridad y una política de incidentes antes de usar datos reales.
21. Estas reglas son requisitos de diseño y no constituyen una declaración de cumplimiento legal o certificación.
