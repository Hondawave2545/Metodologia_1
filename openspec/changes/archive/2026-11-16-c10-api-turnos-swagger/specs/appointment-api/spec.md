# Spec Delta

## Purpose

Contrato HTTP local para operar los turnos del sistema de agenda sobre el servicio de dominio ya implementado y verificado, de modo que las cuatro operaciones existentes puedan demostrarse, probarse y documentarse de punta a punta sin exponer datos reales ni habilitar todavía autenticación o persistencia de producción.

## ADDED Requirements

### Requirement: Descubrimiento del contrato de la API

La API MUST publicar un documento de contrato y una interfaz de documentación interactiva, ambos accesibles sin credenciales, y el documento MUST describir las operaciones de crear, consultar, reprogramar y cancelar turnos.

#### Scenario: El documento de contrato describe las cuatro operaciones

- **Dado** una API en ejecución
- **Cuando** se solicita el documento de contrato
- **Entonces** la respuesta es exitosa
- **Y** el documento describe las operaciones de crear, consultar, reprogramar y cancelar turnos
- **Y** no describe un listado de turnos

#### Scenario: La interfaz de documentación está disponible sin credenciales

- **Dado** una API en ejecución
- **Cuando** se solicita la interfaz de documentación interactiva
- **Entonces** la respuesta es exitosa
- **Y** no se solicitan credenciales

### Requirement: Creación de un turno

La API MUST crear un turno a partir del consultorio, el profesional, el paciente, el servicio, el intervalo y el sillón cuando corresponda. La respuesta MUST ser exitosa y MUST incluir en el cuerpo el turno creado con su identificador, su intervalo y su estado inicial `scheduled`.

#### Scenario: Crear un turno devuelve el turno creado

- **Dado** un consultorio con un profesional, un sillón, un paciente y un servicio activos, y un intervalo libre
- **Cuando** se solicita crear un turno para ese intervalo
- **Entonces** la respuesta es exitosa
- **Y** devuelve el identificador del turno, su intervalo y el estado `scheduled`

#### Scenario: El turno creado bloquea al profesional y al sillón durante su intervalo

- **Dado** un turno creado para un profesional y un sillón entre las 09:00 y las 09:30
- **Cuando** se consulta el turno dentro de su consultorio
- **Entonces** devuelve el mismo intervalo y el mismo estado `scheduled`

#### Scenario: Crear un turno sin sillón en un consultorio que administra sillones

- **Dado** un consultorio que administra sillones
- **Cuando** se solicita crear un turno sin indicar sillón
- **Entonces** la operación se rechaza con un error de validación
- **Y** no se crea ningún turno

### Requirement: Consulta de un turno por consultorio e identificador

La API MUST consultar un turno indicando su consultorio y su identificador, y MUST devolver los datos operativos del turno. Si el identificador no existe o no pertenece al consultorio indicado, MUST responder con un error no revelador.

#### Scenario: Consultar un turno existente devuelve sus datos operativos

- **Dado** un turno creado en el consultorio C1
- **Cuando** se consulta con el identificador de C1 y el identificador del turno
- **Entonces** la respuesta es exitosa
- **Y** devuelve el mismo intervalo, el mismo estado y los mismos recursos asignados

#### Scenario: Consultar un identificador inexistente

- **Dado** un consultorio con recursos registrados
- **Cuando** se consulta un identificador que no existe
- **Entonces** la respuesta es un error de recurso no encontrado
- **Y** no devuelve datos de ningún turno

#### Scenario: Consultar un turno de otro consultorio

- **Dado** un turno que pertenece al consultorio C1
- **Cuando** se consulta con el identificador del consultorio C2 y el identificador de ese turno
- **Entonces** la respuesta es un error de recurso no encontrado
- **Y** no revela datos del turno ni de su paciente

### Requirement: Reprogramación de un turno

La API MUST reprogramar un turno existente dentro de su consultorio actualizando su intervalo. Si el nuevo intervalo entra en conflicto con otro turno activo, MUST responder con un error de conflicto y MUST NOT modificar la reserva original; si el intervalo es inválido, MUST responder con un error de validación.

#### Scenario: Reprogramar a un intervalo libre actualiza el intervalo

- **Dado** un turno activo en el consultorio C1
- **Cuando** se solicita reprogramarlo a un intervalo libre para su profesional y su sillón
- **Entonces** la respuesta es exitosa
- **Y** devuelve el turno con el intervalo nuevo

#### Scenario: Reprogramar a un intervalo en conflicto

- **Dado** un turno activo y otro turno activo del mismo profesional que se solapa con el intervalo propuesto
- **Cuando** se solicita reprogramar el primero
- **Entonces** la respuesta es un error de conflicto
- **Y** el turno original conserva su intervalo anterior
- **Y** la respuesta no contiene datos del paciente del turno en conflicto

#### Scenario: Reprogramar a un intervalo inválido

- **Dado** un turno activo
- **Cuando** se solicita reprogramarlo a un intervalo cuyo inicio no es anterior a su fin
- **Entonces** la respuesta es un error de validación de intervalo
- **Y** el turno original conserva su intervalo anterior

#### Scenario: Reprogramar un turno que no está activo

- **Dado** un turno cancelado
- **Cuando** se solicita reprogramarlo
- **Entonces** la respuesta es un error de recurso no disponible

### Requirement: Cancelación de un turno

La API MUST cancelar un turno activo conservando el registro y marcando su estado como `cancelled`. La respuesta MUST ser exitosa con código `200` y MUST incluir en el cuerpo el turno ya cancelado, para que el cliente vea el estado nuevo sin una segunda consulta. La cancelación no debe responder `204` ni usar `DELETE`. El turno cancelado MUST liberar el profesional y el sillón para una nueva reserva.

#### Scenario: Cancelar un turno conserva el registro y cambia su estado

- **Dado** un turno activo
- **Cuando** se solicita cancelarlo
- **Entonces** la operación es exitosa
- **Y** el turno sigue existiendo con el estado `cancelled`
- **Y** la respuesta incluye el turno cancelado en su cuerpo

#### Scenario: Cancelar un turno libera sus recursos

- **Dado** un turno cancelado para un profesional y un sillón entre las 13:00 y las 13:30
- **Cuando** se crea otro turno para ese mismo profesional y sillón en ese mismo intervalo
- **Entonces** la operación es exitosa
- **Y** el nuevo turno queda creado

#### Scenario: Cancelar un identificador inexistente

- **Dado** un consultorio con recursos registrados
- **Cuando** se solicita cancelar un identificador que no existe
- **Entonces** la respuesta es un error de recurso no encontrado

### Requirement: Mapeo explícito de los errores del dominio

La API MUST traducir cada error del dominio a un código de estado distinto y predecible, y MUST NOT incluir en el cuerpo del error información que identifique al paciente relacionado con un conflicto.

#### Scenario: Conflicto de profesional

- **Dado** un turno activo del profesional
- **Cuando** se intenta crear o reprogramar un turno que se solapa con él
- **Entonces** la respuesta es un error de conflicto
- **Y** el cuerpo del error identifica el recurso en conflicto sin identificar al paciente

#### Scenario: Conflicto de sillón

- **Dado** un turno activo de un sillón para un profesional
- **Cuando** se intenta crear un turno de otro profesional que se solapa con ese sillón
- **Entonces** la respuesta es un error de conflicto
- **Y** el cuerpo del error identifica el sillón como recurso en conflicto

#### Scenario: Intervalo inválido

- **Dado** un intervalo cuyo inicio no es anterior a su fin, o sin zona horaria explícita
- **Cuando** se intenta crear o reprogramar un turno con ese intervalo
- **Entonces** la respuesta es un error de validación de intervalo
- **Y** la respuesta no es un error de conflicto

#### Scenario: Recurso ausente o inactivo

- **Dado** un profesional, sillón, paciente o servicio que no existe o está inactivo
- **Cuando** se intenta crear un turno que lo usa
- **Entonces** la respuesta es un error de recurso no disponible
- **Y** no se crea ningún turno

### Requirement: Aislamiento por consultorio

Todas las operaciones MUST exigir el identificador del consultorio y MUST validar que los recursos asignables pertenezcan a ese consultorio antes de operar.

#### Scenario: Usar un recurso de otro consultorio

- **Dado** un sillón que pertenece al consultorio C1
- **Cuando** se intenta crear en C2 un turno que usa ese sillón
- **Entonces** la operación se rechaza como recurso no disponible
- **Y** no se crea ningún turno

#### Scenario: Recursos homónimos en consultorios distintos

- **Dado** que C1 y C2 tienen cada uno un profesional con el mismo identificador, ambos libres
- **Cuando** se crea en C2 un turno con ese profesional
- **Entonces** la operación es exitosa
- **Y** no se consulta ni se revela la reserva de C1

### Requirement: Ejecución local reproducible con datos ficticios

La API MUST poder iniciarse con el comando documentado, MUST escuchar únicamente en el loopback local, y el script de datos de demostración MUST usar datos exclusivamente ficticios y MUST NOT sobrescribir una base de datos preexistente.

#### Scenario: La API arranca con el comando documentado

- **Dado** un entorno con las dependencias instaladas
- **Cuando** se ejecuta el comando de arranque documentado
- **Entonces** el proceso queda escuchando en el loopback local
- **Y** el documento de contrato y la interfaz de documentación responden

#### Scenario: El script de demostración no sobrescribe datos preexistentes

- **Dado** una base de datos de demostración que ya existe
- **Cuando** se ejecuta el script de datos de demostración
- **Entonces** los registros preexistentes se conservan
- **Y** el script informa los identificadores disponibles

#### Scenario: Los datos de demostración son ficticios

- **Dado** el script de datos de demostración
- **Cuando** se prepara un consultorio con sus recursos
- **Entonces** los nombres, documentos y teléfonos que registra son ficticios
- **Y** el repositorio no contiene datos reales de pacientes

#### Scenario: La suite funciona sin el servidor MCP disponible

- **Dado** un entorno sin conexión al servidor MCP configurado
- **Cuando** se ejecuta la suite de pruebas
- **Entonces** todas las pruebas pasan
- **Y** ninguna prueba depende del servidor MCP
