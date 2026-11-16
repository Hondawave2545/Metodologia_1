# Tareas

## Aprobación y definición

- [x] Confirmar si la administración de sillones se incorpora al alcance del MVP. (Aprobada para este prototipo.)
- [x] Acordar el contrato de errores de validación y conflicto para la interfaz/API. (`InvalidAppointmentInterval` separa errores de entrada; `AppointmentConflict` identifica `professional` o `chair` sin datos del paciente.)
- [x] Seleccionar el mecanismo atómico de exclusión de solapamientos según la arquitectura elegida. (SQLite `BEGIN IMMEDIATE` alrededor de la comprobación y escritura.)

## Dominio y persistencia

- [x] Actualizar los documentos canónicos de modelos, reglas y features si se aprueba la entidad sillón.
- [x] Incorporar la validación de intervalo semiabierto y de inicio anterior al fin.
- [x] Implementar la comprobación de conflictos del profesional en creación y reprogramación.
- [x] Implementar la asignación y comprobación de conflictos del sillón en consultorios que lo administren.
- [x] Asegurar aislamiento por consultorio y validar pertenencia/estado de recursos.
- [x] Hacer atómica la comprobación y escritura para prevenir conflictos concurrentes.
- [x] Excluir el turno original al validar una reprogramación.
- [x] Devolver errores explícitos sin información del turno o paciente en conflicto.

## Verificación

- [x] Añadir pruebas automatizadas para cada escenario de `specs/agenda-turnos/spec.md`.
- [x] Probar creación y reprogramación concurrentes para el mismo profesional y sillón.
- [x] Verificar que turnos cancelados liberen recursos y turnos activos no.
- [x] Verificar turnos adyacentes, intervalos inválidos y conversión de zona horaria.
- [x] Verificar aislamiento entre consultorios con identificadores locales coincidentes.
- [x] Ejecutar las pruebas y verificaciones existentes pertinentes y registrar cualquier limitación.
- [x] Sincronizar los requisitos aprobados con `openspec/specs/agenda-turnos/spec.md` antes de archivar el change.
- [x] Archivar el change completado en `openspec/archive/2026-10-15-crear-turno-sin-solapamientos/`.

## Verificación y limitaciones

- `python -m unittest discover -s tests -v`: 18 pruebas aprobadas.
- Los escenarios Gherkin del change están cubiertos por pruebas de servicio SQLite.
- No había aplicación ni framework de API en el repositorio; el módulo es un servicio de dominio con persistencia local SQLite y requiere integración antes de un piloto.
- Las fechas se reciben como `datetime` con zona horaria explícita y se normalizan a UTC. La resolución de la hora local usando la zona IANA configurada debe realizarla la capa de entrada antes de invocar el servicio.
