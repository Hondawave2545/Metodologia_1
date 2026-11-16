# Guía para Claude

## Contexto del producto
- Lee los documentos pertinentes de `knowledge-base/` antes de trabajar. Allí están la visión, actores, modelos, reglas y funcionalidades canónicas.
- Usa `docs/discovery/informe-discovery.md` como investigación de mercado: sus conclusiones dependen de la evidencia y las fechas que allí se registran.
- El alcance de MVP en `knowledge-base/vision.md` es provisional y requiere validación. No lo conviertas en una decisión aprobada ni amplíes su alcance sin indicación.

## Skills del proyecto
- `api-turnos`: guía de trabajo en la API HTTP de turnos (`src/api/`). Archivo: `.opencode/skills/api-turnos/SKILL.md`.
  Usala siempre que la tarea toque la API de turnos, Swagger, `/docs`, `/openapi.json`, el contrato HTTP de citas o los tests de FastAPI del repositorio.
  Referencias: `.opencode/skills/api-turnos/references/gotchas.md` y `.opencode/skills/api-turnos/references/contrato-http.md`.

## Reglas
- Responde en español, salvo que el usuario pida otro idioma.
- Distingue requisitos aprobados, hipótesis y evidencia. No inventes funcionalidades de competidores ni datos o referencias.
- Protege la información de pacientes con minimización de datos, acceso por rol y registro de acciones pertinentes. No declares cumplimiento normativo sin validación especializada.
- Sigue `knowledge-base/features.md`, `knowledge-base/reglas-de-negocio.md` y `CHANGES.md`; señala conflictos de alcance antes de resolverlos por cuenta propia.
- Revisa archivos y cambios existentes antes de editarlos; limita el trabajo a lo solicitado y valida el código con las herramientas y pruebas disponibles.
- **Datos ficticios siempre:** nunca almacenar datos reales de pacientes en el repositorio, en tests, ejemplos ni capturas. Usar nombres, documentos y teléfonos inventados.
- **Semántica de agenda:** los turnos son intervalos semiabiertos `[inicio, fin)` y solo los estados `scheduled` y `confirmed` bloquean profesional y sillón. No cambiar esta semántica sin un change aprobado en `openspec/`.
- Mantén sincronizadas estas instrucciones con `AGENTS.md` cuando cambien las reglas compartidas.
