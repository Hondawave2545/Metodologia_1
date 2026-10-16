# Flujos principales

**Estado:** flujos candidatos del MVP; validar con consultorios piloto. Los pasos 1 a 3 de "Crear turno" y "Reprogramar" ya están implementados y probados en el prototipo.

## 1. Crear turno

1. Recepción elige consultorio, profesional, paciente, servicio y (si el consultorio administra sillones) un sillón activo.
2. El sistema valida que todos los recursos pertenezcan al mismo consultorio y estén activos.
3. El sistema valida el intervalo: el inicio debe ser anterior al fin. Un intervalo vacío o invertido es un error de validación, no un conflicto.
4. Dentro de una operación atómica, busca turnos `scheduled` o `confirmed` que se solapen con el profesional o el sillón.
5. Si hay conflicto, rechaza la operación completa con `appointment_conflict` indicando el recurso (`professional` o `chair`), sin datos del otro paciente.
6. Si no hay conflicto, guarda el turno como `scheduled`, con actor y fecha.

## 2. Reprogramar turno

Igual que "Crear turno", excluyendo el turno original de su propia búsqueda de conflictos. Si falla, el turno original queda intacto.

## 3. Cancelar turno

El turno pasa a `cancelled` y deja de bloquear recursos. El registro se conserva; no se borra.

## 4. Confirmar y recordar (puerta de decisión)

1. Antes del turno, el sistema envía un recordatorio por el canal configurado y permitido para ese paciente (WhatsApp si se valida).
2. El paciente confirma o solicita cambio.
3. Se registra canal, propósito, fecha y resultado de entrega. Un envío fallido **no** cambia el estado del turno y es visible para el operador.

## 5. Registrar resultado

Después del horario, el profesional o recepción marca el turno como `completed` o `no_show`. Ninguno de los dos estados bloquea recursos.

## Estados del turno

`scheduled → confirmed → completed`, con salidas a `cancelled` o `no_show`. Las transiciones permitidas deben ser explícitas; un turno cancelado no se reactiva: se crea uno nuevo.
