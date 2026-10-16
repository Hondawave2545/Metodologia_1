# Registro de decisiones

Cada decisión indica su estado. Las decisiones de producto son **hipótesis** hasta completar la Fase 0 de `CHANGES.md`.

| # | Decisión | Estado | Motivo | Fuente |
|---|---|---|---|---|
| D-01 | Los turnos son intervalos semiabiertos `[inicio, fin)`; los turnos consecutivos no se solapan. | Aprobada (prototipo) | Permite encadenar turnos sin buffer artificial. | `openspec/changes/archive/.../design.md` |
| D-02 | Solo `scheduled` y `confirmed` bloquean recursos. | Aprobada (prototipo) | Un turno cancelado debe liberar el horario. | `reglas-de-negocio.md` #7 |
| D-03 | El sillón es un recurso opcional por consultorio; si el consultorio los administra, cada turno requiere uno. | Aprobada para el prototipo; inclusión definitiva en el MVP sujeta a validación | Hipótesis de diferenciación; AgendaPro y ClinIA mencionan sillones, otros competidores no lo documentan. | Informe, sección C |
| D-04 | Validar y escribir en una sola transacción atómica (SQLite `BEGIN IMMEDIATE`). | Aprobada (prototipo) | Evita doble reserva ante concurrencia. | `design.md` |
| D-05 | Guardar instantes en UTC y conservar la zona IANA del consultorio. | Aprobada | Evita ambigüedad en cambios de horario. | `modelos-de-datos.md` |
| D-06 | Sin historia clínica ni odontograma en el primer MVP. | Hipótesis; revisar antes del piloto | Reduce superficie de datos sensibles. Riesgo: los competidores especializados puntúan alto en funcionalidad clínica. | Informe, secciones C y D |
| D-07 | WhatsApp como canal de recordatorios, condicionado a validar proveedor, costo y consentimiento. | Puerta de decisión (P1) | Meta cobra por mensaje; el consentimiento es obligatorio. | `features.md` MVP-08 |
| D-08 | Usar DentalSoft como benchmark principal y AgendaPro y Dentalink como referencias. | Provisional | Resultado de la matriz de puntuación; requiere demos. | Informe, sección D |
| D-09 | Un conflicto de agenda responde con el tipo de recurso, nunca con datos del otro paciente. | Aprobada | Privacidad. | `proposal.md` |
