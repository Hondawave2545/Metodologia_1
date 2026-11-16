# Especificación: disponibilidad de recursos en turnos

## Requisitos

### Requirement: Rechazo de turnos que solapan un recurso

El sistema MUST rechazar la creación o reprogramación si el intervalo se cruza con otro turno en estado `scheduled` o `confirmed` del mismo profesional. Si el consultorio administra sillones, también MUST rechazar el uso solapado del sillón seleccionado, incluso cuando el profesional sea distinto. La validación y la escritura MUST ser atómicas. El rechazo MUST dejar intactas las reservas existentes y no revelar datos del paciente relacionado con el conflicto.

#### Scenario: Crear un turno disponible

- **Dado** que el profesional P1 y el sillón S1 están libres entre las 09:00 y las 09:30 en el consultorio C1
- **Cuando** recepción crea un turno para ese intervalo, P1 y S1
- **Entonces** el sistema guarda el turno con estado `scheduled`
- **Y** el turno ocupa P1 y S1 durante `[09:00, 09:30)`

#### Scenario: Rechazar solapamiento del profesional

- **Dado** que existe un turno `confirmed` para P1 de 09:00 a 09:30 en C1
- **Y** que P2 y el sillón S2 están libres de 09:15 a 09:45 en C1
- **Cuando** recepción intenta crear un turno de 09:15 a 09:45 con P1 y S2
- **Entonces** el sistema rechaza la operación con `appointment_conflict` para el recurso `professional`
- **Y** no crea el nuevo turno ni modifica el turno existente
- **Y** la respuesta no contiene datos del paciente del turno existente

#### Scenario: Rechazar solapamiento del sillón con otro profesional

- **Dado** que existe un turno `scheduled` para P1 y S1 de 10:00 a 10:30 en C1
- **Y** que P2 está libre de 10:15 a 10:45 en C1
- **Cuando** recepción intenta crear un turno de 10:15 a 10:45 con P2 y S1
- **Entonces** el sistema rechaza la operación con `appointment_conflict` para el recurso `chair`
- **Y** no crea el nuevo turno ni modifica el turno existente

### Requirement: Límites de intervalo y liberación de recursos

El sistema MUST interpretar los turnos como intervalos semiabiertos `[inicio, fin)`. Un turno cancelado MUST liberar sus recursos. En la reprogramación, el turno original MUST excluirse de la propia búsqueda de conflictos. El sistema MUST rechazar un intervalo cuyo inicio sea igual o posterior a su fin como error de validación.

#### Scenario: Permitir turnos consecutivos en el límite

- **Dado** que existe un turno `confirmed` para P1 y S1 de 11:00 a 11:30 en C1
- **Cuando** recepción crea otro turno para P1 y S1 de 11:30 a 12:00
- **Entonces** el sistema guarda el segundo turno
- **Y** ambos turnos permanecen sin solapamiento

#### Scenario: Permitir reservar un recurso liberado por cancelación

- **Dado** que existe un turno `cancelled` para P1 y S1 de 13:00 a 13:30 en C1
- **Cuando** recepción crea otro turno para P1 y S1 de 13:00 a 13:30
- **Entonces** el sistema guarda el nuevo turno

#### Scenario: Rechazar intervalo vacío

- **Dado** que P1 y S1 están libres de 14:00 a 14:30 en C1
- **Cuando** recepción intenta crear un turno cuyo inicio y fin son ambos las 14:00
- **Entonces** el sistema rechaza la operación con un error de validación de intervalo
- **Y** no devuelve `appointment_conflict`
- **Y** no crea ningún turno

### Requirement: Aislamiento de recursos por consultorio

El sistema MUST comprobar conflictos únicamente entre turnos del mismo consultorio y MUST validar que los recursos asignados pertenezcan a ese consultorio. Un turno que incluya un sillón en un consultorio que administra sillones MUST usar un sillón activo de ese consultorio. Si el consultorio administra sillones, crear un turno MUST requerir un sillón.

#### Scenario: No tratar como conflicto un recurso homónimo de otro consultorio

- **Dado** que el consultorio C1 tiene un turno para su profesional P1 y sillón S1 de 15:00 a 15:30
- **Y** que C2 es otro consultorio con sus propios recursos P1 y S1 disponibles
- **Cuando** recepción crea en C2 un turno para su P1 y S1 de 15:00 a 15:30
- **Entonces** el sistema guarda el turno en C2
- **Y** no consulta ni revela la reserva de C1

#### Scenario: Rechazar un recurso perteneciente a otro consultorio

- **Dado** que el sillón S1 pertenece al consultorio C1
- **Y** que C2 administra sillones pero no tiene un sillón con identificador S1
- **Cuando** recepción intenta reservar en C2 usando S1 de 15:00 a 15:30
- **Entonces** el sistema rechaza la operación como recurso no disponible
- **Y** no crea ningún turno
