# Actores y permisos

**Estado:** propuesta inicial para el MVP candidato; validar con consultorios piloto.

## Actores

| Actor | Responsabilidad | Acceso candidato |
|---|---|---|
| Titular / administrador del consultorio | Configura el espacio, gestiona usuarios, profesionales y servicios, y supervisa la agenda. | Administración y datos operativos de su consultorio. |
| Recepción | Registra pacientes y gestiona turnos en nombre del consultorio. | Datos de contacto mínimos y agenda; sin administración de usuarios ni configuración sensible por defecto. |
| Profesional odontológico | Consulta su agenda y registra el resultado operativo del turno. | Agenda propia y datos mínimos necesarios para atender; el MVP no incluye historia clínica. |
| Paciente | Recibe información de sus turnos y puede confirmar o solicitar cambios según el canal habilitado. | Sus propios turnos a través de una interacción verificada; el portal de autogestión no es requisito inicial. |
| Operador técnico del servicio | Mantiene la plataforma y atiende incidentes autorizados. | Acceso excepcional, limitado, justificado y auditable; nunca acceso rutinario a datos clínicos. |

## Límites de autorización

- Cada consultorio constituye un límite de datos; usuarios y consultas deben estar asociados al consultorio correspondiente.
- Una persona puede pertenecer a más de un consultorio únicamente si se autoriza esa relación de forma explícita.
- La recepción solo necesita los datos requeridos para coordinar turnos.
- El profesional accede a su agenda y a información operativa necesaria; cualquier acceso clínico futuro requiere un modelo de permisos separado.
- Las acciones administrativas y los accesos de soporte deben quedar sujetos a controles y registro.
- La identidad del paciente debe verificarse antes de exponer, cambiar o cancelar información de sus turnos.

## Pendiente de validar

Delegación entre profesionales, permisos de recepción por sucursal, autogestión del paciente, acceso de tutores y permisos de soporte requieren validación antes de incorporarse al MVP.
