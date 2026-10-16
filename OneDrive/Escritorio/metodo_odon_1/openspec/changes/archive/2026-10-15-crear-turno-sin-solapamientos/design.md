# Diseño: crear turnos sin solapamientos

## Contexto

El modelo conceptual define `Appointment` con consultorio, profesional, paciente, servicio, inicio, fin y estado. Las reglas requieren prevenir de forma atómica el solapamiento del profesional y, cuando el consultorio administra sillones, el del sillón asignado.

## Decisiones

### Intervalos semiabiertos

Representar cada turno como `[start_at, end_at)`. Dos turnos se solapan si:

```text
existing.start_at < requested.end_at
AND existing.end_at > requested.start_at
```

Por lo tanto, `[09:00, 09:30)` y `[09:30, 10:00)` son compatibles. `start_at` debe ser anterior a `end_at`; intervalos vacíos o invertidos se rechazan como entrada inválida.

### Recursos ocupados

- El profesional siempre es un recurso exclusivo durante el turno.
- El sillón es opcional a nivel de consultorio. Si el consultorio administra sillones, la reserva selecciona un sillón activo de ese mismo consultorio; en un consultorio sin sillones configurados, el turno puede no tener sillón.
- Un turno ocupa los recursos mientras su estado sea `scheduled` o `confirmed`. Los turnos cancelados, completados o marcados `no_show` no bloquean reservas nuevas.
- La reprogramación valida contra otros turnos y excluye el identificador del turno que se está reprogramando.
- Toda consulta de conflicto se restringe al `clinic_id` correspondiente; no se comparan recursos de consultorios distintos.

### Atomicidad y resultado

Validar la reserva y persistirla como una única operación atómica. El prototipo SQLite inicia `BEGIN IMMEDIATE` antes de leer los conflictos y mantiene la transacción hasta insertar o reprogramar. Esto serializa las escrituras competidoras en la base de datos del prototipo; una comprobación previa separada de la escritura no es suficiente frente a concurrencia. La estrategia de persistencia de producción sigue pendiente.

Si cualquier recurso entra en conflicto, rechazar la operación completa con un error de negocio identificable (`appointment_conflict`), indicando el tipo de recurso en conflicto (`professional` o `chair`) y sin incluir datos del turno o del paciente existente. No actualizar ni borrar la reserva que ocasionó el conflicto.

La validación de formato de intervalo debe distinguirse de un conflicto: un intervalo inválido devuelve un error de validación, no `appointment_conflict`.

### Tiempo

Comparar instantes normalizados, almacenados en UTC según el modelo conceptual. Interpretar horarios locales usando la zona horaria del consultorio antes de convertirlos; la interfaz presenta el error y el turno en la zona horaria configurada.

## Flujo propuesto

1. Autenticar al actor y verificar su pertenencia y permiso en el consultorio.
2. Validar que profesional, paciente, servicio y, si aplica, sillón pertenezcan al mismo consultorio y estén activos.
3. Normalizar y validar el intervalo.
4. Dentro de la operación atómica, buscar turnos bloqueantes que se solapen para el profesional y, si fue asignado, para el sillón.
5. Si hay conflictos, rechazar sin mutaciones y devolver el tipo de recurso afectado.
6. Si no hay conflictos, guardar el turno (o los nuevos datos del turno reprogramado) y el actor/fecha requeridos para la trazabilidad.

## Modelo

La propuesta de sillones fue aprobada para este prototipo. El esquema SQLite implementa `chairs` y la referencia opcional `appointments.chair_id`, y los documentos canónicos modelan `Chair`. Definir unicidad de nombres o códigos visibles dentro del consultorio queda pendiente.

## Alternativas descartadas

- **Comprobar y luego guardar sin transacción:** permite que dos solicitudes concurrentes pasen la misma comprobación y creen un solapamiento.
- **Tratar turnos adyacentes como conflicto:** impide encadenar turnos sin que la evidencia del producto requiera un buffer.
- **Incluir turnos cancelados en la comprobación:** mantendría bloqueados recursos que ya se liberaron.
- **Devolver datos del turno existente para explicar el error:** revelaría información de otro paciente innecesariamente.

## Límites y riesgos

- SQLite con `BEGIN IMMEDIATE` implementa la exclusión concurrente en este prototipo. La arquitectura y la persistencia de producción quedan pendientes.
- La administración de sillones fue aprobada para este prototipo; su inclusión definitiva en el MVP sigue sujeta a validación del producto.
- Reglas temporales y de zona horaria deben cubrir casos de límites locales y conversiones UTC.
