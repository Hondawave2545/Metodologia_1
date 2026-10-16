# Descripción del producto

**Estado:** descripción funcional del MVP candidato. Complementa `vision.md`; no reemplaza la validación con usuarios.

## Qué es

Un sistema web de **gestión de turnos y agenda de pacientes** para consultorios odontológicos pequeños de Argentina (uno a cinco profesionales). Su foco es que la agenda sea **confiable**: que nunca se asigne dos veces el mismo profesional o sillón en el mismo horario, y que los pacientes reciban confirmaciones y recordatorios.

## Qué resuelve

- Coordinar la agenda de varios profesionales (y, si el consultorio los administra, de varios sillones) sin conflictos.
- Reducir el trabajo manual de confirmar turnos.
- Mantener un registro operativo de quién creó, cambió o canceló cada turno.

## Qué NO es (en el primer MVP)

No es una suite clínica: no incluye historia clínica, odontograma, facturación electrónica, obras sociales, pagos ni portal del paciente. Esas funciones son estándar en competidores como DentalSoft, ClinIA o Dentalink, y se evalúan después de validar el flujo central (ver `features.md` y `decisiones.md`).

## Diferenciación candidata (hipótesis)

Según la sección C del informe de Discovery:
1. Prevención atómica de doble reserva por profesional **y** sillón, con errores explícitos que no filtran datos de otros pacientes.
2. Recordatorios por WhatsApp con consentimiento y fallos visibles, accesibles sin depender de un plan alto.
3. Precio y alcance transparentes.

Ninguna está validada con usuarios; deben contrastarse contra DentalSoft y AgendaPro mediante demos.

## Estado de implementación

Existe un prototipo del dominio de turnos (`src/appointments.py`, SQLite) que implementa y prueba el change archivado *crear turno sin solapamientos*. No hay interfaz, autenticación ni API.
