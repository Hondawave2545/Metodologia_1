# Spec Delta

## ADDED Requirements

### Requirement: Consulta de disponibilidad de un intervalo

La API MUST consultar si un intervalo está libre para un profesional y para un sillón cuando el consultorio administra sillones. La respuesta MUST ser exitosa y MUST indicar si el intervalo está disponible y qué tipo de recurso lo ocupa, sin revelar datos de ningún turno ni de su paciente.

#### Scenario: Consultar un intervalo libre

- **Dado** un consultorio con un profesional y un sillón activos, y un intervalo sin turnos activos
- **Cuando** se solicita la disponibilidad de ese intervalo
- **Entonces** la respuesta es exitosa
- **Y** el cuerpo indica que el intervalo está disponible
- **Y** no indica ningún recurso en conflicto

#### Scenario: Consultar un intervalo ocupado por el profesional

- **Dado** un turno activo del profesional que se solapa con el intervalo consultado
- **Cuando** se solicita la disponibilidad de ese intervalo
- **Entonces** la respuesta es exitosa
- **Y** el cuerpo indica que el intervalo no está disponible
- **Y** el recurso en conflicto es el profesional
- **Y** la respuesta no contiene datos del paciente del turno en conflicto

#### Scenario: Consultar un intervalo ocupado por el sillón

- **Dado** un turno activo de un sillón que se solapa con el intervalo consultado
- **Cuando** se solicita la disponibilidad de ese intervalo
- **Entonces** la respuesta es exitosa
- **Y** el cuerpo indica que el intervalo no está disponible
- **Y** el recurso en conflicto es el sillón

#### Scenario: Un turno cancelado no bloquea el intervalo

- **Dado** un turno cancelado que se solapa con el intervalo consultado
- **When** se solicita la disponibilidad de ese intervalo
- **Entonces** la respuesta indica que el intervalo está disponible

#### Scenario: Consultar un intervalo inválido

- **Dado** un intervalo cuyo inicio no es anterior a su fin, o sin zona horaria explícita
- **When** se solicita la disponibilidad de ese intervalo
- **Entonces** la respuesta es un error de validación de intervalo
- **Y** la respuesta no es un error de conflicto

#### Scenario: Consultar la disponibilidad de un profesional ausente o inactivo

- **Dado** un profesional que no existe o está inactivo
- **When** se solicita la disponibilidad de un intervalo para ese profesional
- **Entonces** la respuesta es un error de recurso no disponible

#### Scenario: Consultar la disponibilidad de un profesional de otro consultorio

- **Dado** un profesional que pertenece a otro consultorio
- **When** se solicita la disponibilidad de un intervalo para ese profesional en este consultorio
- **Entonces** la respuesta es un error de recurso no disponible
- **Y** no revela si ese profesional tiene reservas en otro consultorio

#### Scenario: Consultar la disponibilidad sin sillón en un consultorio que administra sillones

- **Dado** un consultorio que administra sillones
- **When** se solicita la disponibilidad de un intervalo sin indicar sillón
- **Entonces** la operación es rechazada con un error de validación

## MODIFIED Requirements

### Requirement: Descubrimiento del contrato de la API

La API MUST publicar un documento de contrato y una interfaz de documentación interactiva, ambos accesibles sin credenciales, y el documento MUST describir las operaciones de crear, consultar, reprogramar y cancelar turnos, además de la consulta de disponibilidad de un intervalo.

#### Scenario: El documento de contrato describe las cuatro operaciones

- **Dado** una API en ejecución
- **Cuando** se solicita el documento de contrato
- **Entonces** la respuesta es exitosa
- **Y** el documento describe las operaciones de crear, consultar, reprogramar y cancelar turnos
- **Y** no describe un listado de turnos

#### Scenario: El documento de contrato describe la consulta de disponibilidad

- **Dado** una API en ejecución
- **Cuando** se solicita el documento de contrato
- **Entonces** la respuesta es exitosa
- **Y** el documento describe la operación de consultar la disponibilidad de un intervalo

#### Scenario: La interfaz de documentación está disponible sin credenciales

- **Dado** una API en ejecución
- **Cuando** se solicita la interfaz de documentación interactiva
- **Entonces** la respuesta es exitosa
- **Y** no se solicitan credenciales
