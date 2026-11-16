# Crear turnos sin solapamientos

## Estado

Implementado como prototipo funcional en `src/appointments.py`, con cobertura automatizada en `tests/test_appointments.py`. La integración con una aplicación y su persistencia de producción queda pendiente.

## Por qué se eligió este change

Pertenece al MVP recomendado en la sección D del informe de Discovery (imprescindible: prevención de solapamientos por profesional y sillón) y corresponde a la feature MVP-07 de `knowledge-base/features.md`. Tiene reglas de negocio verificables (intervalos semiabiertos, estados que bloquean, aislamiento por consultorio) y es lo bastante chico como para terminarse: una sola funcionalidad, no un módulo. Además, es la base de la diferenciación candidata frente a los competidores analizados.

## Problema

La regla de negocio actual prohíbe solapamientos para un profesional, pero no especifica una validación verificable que contemple también la disponibilidad de un sillón odontológico. Sin una decisión atómica al reservar o reprogramar, dos operaciones simultáneas podrían asignar el mismo recurso a turnos incompatibles.

## Cambio propuesto

Al crear o reprogramar un turno, validar que el intervalo sea válido y que no se cruce con otro turno activo del mismo profesional ni, cuando el consultorio administra sillones, del mismo sillón. Si existe un conflicto, rechazar la operación sin guardar parcialmente el turno e informar el recurso ocupado sin revelar información de otro paciente.

Los intervalos se interpretan como `[inicio, fin)`: un turno que termina exactamente cuando comienza otro no constituye solapamiento. La comprobación debe ser atómica para que reservas concurrentes no puedan ocupar el mismo recurso.

## Alcance

- Validar intervalos y solapamientos de turnos al crear y reprogramar.
- Aplicar el conflicto al profesional y al sillón dentro del mismo consultorio.
- Considerar bloqueantes únicamente los turnos en estado `scheduled` o `confirmed`.
- Permitir reservas consecutivas en el límite exacto de los intervalos.
- Mantener la separación de datos por consultorio y excluir el turno que se está reprogramando de su propia comprobación.

La gestión de sillones quedó aprobada para este prototipo y se incorporó a los modelos y reglas canónicos. En consultorios que no administren sillones, la reserva valida el profesional sin requerir sillón.

## Fuera de alcance

- Cambios en la duración del servicio, buffers entre turnos o configuración de bloques.
- Lista de espera, sobrecupos, excepciones de horarios y asignación automática de sillón.
- Cambios al flujo de notificaciones, pagos o historia clínica.
- Cambios a la política de transición de estados fuera de determinar qué turnos ocupan recursos.

## Criterios de aceptación

1. No se guarda un turno cuando se solapa con otro turno activo del mismo profesional.
2. Si se administran sillones, no se guarda un turno cuando el sillón seleccionado se solapa con otro turno activo, aunque el profesional sea distinto.
3. Una solicitud rechazada no deja un turno parcial ni altera la reserva existente.
4. Los turnos adyacentes cuyos extremos coinciden pueden guardarse.
5. Un turno cancelado no bloquea el recurso; al reprogramar un turno, este no entra en conflicto consigo mismo.
6. Las operaciones concurrentes sobre el mismo recurso no pueden confirmar ambas reservas solapadas.
7. La respuesta de conflicto no expone identidad ni datos del paciente que tiene la reserva existente.

## Riesgos y límites de esta implementación

- La aprobación de sillones aplica a este prototipo; su inclusión definitiva en el MVP depende de la validación del producto.
- SQLite con `BEGIN IMMEDIATE` garantiza la atomicidad para este prototipo local. La persistencia de producción requiere una decisión de arquitectura.
- La resolución de horas locales según la zona IANA configurada corresponde a la capa de entrada; el servicio acepta fechas con zona horaria y las normaliza a UTC.
- El módulo aún debe integrarse con la autenticación, la autorización y la interfaz/API de la aplicación, que no existen en el repositorio.
