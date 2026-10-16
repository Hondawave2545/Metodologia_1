# Instrucciones del proyecto

## Fuente de verdad
- Antes de proponer cambios, consulta los documentos aplicables de `knowledge-base/`; son la referencia canónica del producto.
- `docs/discovery/informe-discovery.md` contiene evidencia de mercado, no requisitos aprobados. Conserva sus fuentes y distingue hechos, inferencias e hipótesis.
- El MVP descrito en `knowledge-base/vision.md` es una hipótesis pendiente de validación. No la presentes como decisión aprobada.

## Reglas de trabajo
- Comunícate en español salvo que el usuario solicite otro idioma; conserva nombres técnicos y términos del código cuando corresponda.
- Mantén los cambios alineados con `knowledge-base/features.md`, `knowledge-base/reglas-de-negocio.md` y `CHANGES.md`. Si una solicitud contradice estas fuentes, señala la discrepancia antes de cambiar el alcance.
- No inventes capacidades, precios, fuentes ni requisitos legales. Cita evidencia para afirmaciones de mercado y marca lo no verificado.
- Trata los datos de pacientes como sensibles: aplica minimización, control de acceso y trazabilidad. No afirmes cumplimiento legal sin revisión especializada.
- Realiza solo los cambios solicitados; conserva el estilo y las convenciones del repositorio. Antes de modificar archivos, inspecciona su contenido y estado para preservar trabajo existente.
- Si implementas código, valida con las pruebas y herramientas existentes más acotadas que cubran el cambio; no agregues dependencias sin necesidad.
- **Datos ficticios siempre:** nunca almacenar datos reales de pacientes en el repositorio, en tests, ejemplos ni capturas. Usar nombres, documentos y teléfonos inventados.
- **Semántica de agenda:** los turnos son intervalos semiabiertos `[inicio, fin)` y solo los estados `scheduled` y `confirmed` bloquean profesional y sillón. No cambiar esta semántica sin un change aprobado en `openspec/`.
- Mantén este archivo y `CLAUDE.md` concisos; actualízalos cuando cambien las reglas del proyecto.
