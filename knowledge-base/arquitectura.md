# Arquitectura

**Estado:** solo está decidido lo necesario para el prototipo. La arquitectura de producción está **pendiente** (ver `preguntas-abiertas.md`).

## Estado actual (prototipo)

- **Lenguaje:** Python, solo librería estándar.
- **Capa de dominio:** `AppointmentRepository` en `src/appointments.py`, con operaciones para registrar consultorio, profesional, sillón, paciente y servicio, y para crear, reprogramar, cancelar y consultar turnos.
- **Persistencia:** SQLite local.
- **Exclusión concurrente:** la comprobación de conflictos y la escritura ocurren dentro de una transacción `BEGIN IMMEDIATE`, que serializa las escrituras competidoras. Una comprobación previa separada de la escritura no es suficiente.
- **Errores de negocio:** `InvalidAppointmentInterval`, `AppointmentConflict` (con el recurso en conflicto), `ResourceUnavailable`, `ChairRequired` y `AppointmentNotFound`.
- **Tiempo:** el servicio recibe `datetime` con zona horaria explícita y los normaliza a UTC. Resolver la hora local con la zona IANA del consultorio corresponde a la capa de entrada.
- **Pruebas:** `unittest`, un test o más por escenario del spec, incluidas pruebas de concurrencia.

## Principios

- Separación de datos por consultorio (tenant) comprobada en cada operación.
- Datos mínimos: sin historia clínica en el MVP.
- Errores explícitos: nunca se aparenta éxito ante un fallo.
- Los permisos se validan en el servidor, no se derivan de datos enviados por el cliente.

## Pendiente de decidir

Persistencia de producción, API y framework, identidad y autenticación, estrategia integral de multi-tenancy, proveedor de mensajería, monitoreo, copias de seguridad y retención de datos.
