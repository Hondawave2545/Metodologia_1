# Modelos de datos

**Estado:** modelo conceptual inicial para el MVP candidato. No es un esquema físico ni una aprobación de arquitectura.

## Principios

- Separar datos por consultorio (tenant) y comprobar el límite de acceso en cada operación.
- Recopilar solo datos necesarios para coordinar turnos. Los datos de salud son sensibles; el MVP candidato no define historia clínica odontológica.
- Usar identificadores estables, fechas auditables y relaciones explícitas.
- Guardar instantes en UTC y conservar la zona horaria IANA configurada por el consultorio para mostrar y calcular horarios locales.
- Definir retención, exportación, eliminación y requisitos legales con asesoramiento especializado antes de operar con datos reales.

## Entidades

### Consultorio (`Clinic`)

- `id`
- `name`
- `timezone` (zona IANA; por ejemplo, la correspondiente a la ubicación del consultorio)
- datos de contacto del consultorio, solo si son necesarios
- fechas de creación y actualización

### Usuario y pertenencia (`User`, `ClinicMembership`)

- `User`: `id`, identificador de acceso, estado y fechas relevantes.
- `ClinicMembership`: `clinic_id`, `user_id`, rol (`owner`, `receptionist`, `professional`), estado y permisos adicionales explícitos, si se validan.
- La pertenencia define el ámbito de acceso; no derivar permisos únicamente de datos enviados por el cliente.

### Profesional (`Professional`)

- `id`, `clinic_id`, nombre visible, estado y, si aplica, relación con `user_id`.
- La información profesional adicional queda fuera del esquema mínimo hasta validar su necesidad.

### Sillón (`Chair`)

- `id`, `clinic_id`, identificador visible y estado.
- Es un recurso opcional por consultorio; solo los consultorios que administran sillones requieren asignar uno a cada turno.

### Servicio (`Service`)

- `id`, `clinic_id`, nombre, duración en minutos, estado y descripción operativa opcional.
- Precio no requerido para el MVP; incorporar solo si se aprueba alcance de cobros.

### Paciente (`Patient`)

- `id`, `clinic_id`, nombre, medio de contacto y estado.
- Datos mínimos para identificar y contactar; teléfono o correo solo cuando se necesite para el canal habilitado.
- Preferencias y constancia de consentimiento por canal cuando correspondan; no almacenar datos de salud en campos libres de contacto.

### Regla de disponibilidad (`AvailabilityRule`)

- `id`, `clinic_id`, `professional_id`, día de semana, hora local de inicio y fin, vigencia y zona horaria aplicable.
- Las excepciones, cierres y bloqueos de agenda deben representarse explícitamente (`ScheduleException`) si se incluyen en implementación.

### Turno (`Appointment`)

- `id`, `clinic_id`, `professional_id`, `patient_id`, `service_id`.
- Referencia opcional `chair_id`, que debe pertenecer al mismo consultorio y estar activa cuando el consultorio administra sillones.
- Inicio y fin como instantes, con zona de presentación definida por el consultorio.
- Estado (`scheduled`, `confirmed`, `cancelled`, `completed`, `no_show`), canal de origen opcional y marcas temporales.
- Registro de quién crea o modifica y motivo de cancelación cuando se capture.
- No incluir diagnóstico ni notas clínicas en el MVP candidato.

### Notificación (`Notification`)

- `id`, `clinic_id`, `appointment_id`, canal, propósito, estado de entrega, marca temporal, referencia del proveedor y error operacional acotado.
- No guardar contenido innecesario del mensaje ni credenciales del proveedor.
- Mantener la información suficiente para seguimiento y auditoría, de acuerdo con una política de retención por definir.

### Evento de auditoría (`AuditEvent`)

- `id`, `clinic_id`, actor, acción, tipo e identificador de entidad, fecha UTC y metadatos mínimos del cambio.
- No copiar datos clínicos ni secretos a los eventos.

## Relaciones principales

- Un consultorio tiene profesionales, usuarios asociados, servicios, pacientes y reglas de agenda.
- Un consultorio que administra sillones tiene uno o más sillones propios.
- Una pertenencia vincula un usuario con un consultorio y un rol.
- Un turno vincula un único consultorio, profesional, paciente y servicio, y opcionalmente un sillón.
- Un turno puede tener múltiples notificaciones y eventos de auditoría.

## Decisiones pendientes

El prototipo de reservas usa SQLite con comprobación y escritura dentro de `BEGIN IMMEDIATE`; la arquitectura de persistencia de producción, identidad y autenticación, estrategia integral de multi-tenancy, tratamiento de duplicados de pacientes, recurrencia y excepciones de agenda, política de retención, exportación y eliminación siguen pendientes.
