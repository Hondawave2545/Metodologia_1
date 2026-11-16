# Registro de Skills del Proyecto

- **discovery-research**: Utilizada para la investigación de mercado, análisis de plataformas de salud (Dentalink, AgendaPro, etc.) y contraste de fuentes. (Etapa: Discovery)
- **kb-creator**: Utilizada para estructurar la base de conocimiento canónica (visión, actores, modelos de datos, reglas de negocio). (Etapa: Fundación)
- **roadmap-generator**: Utilizada para armar el archivo `CHANGES.md` y definir las fases del proyecto. (Etapa: Planificación)
- **OpenSpec**: Utilizada para el ciclo OPSX del primer cambio (propuesta, diseño, tareas y especificación de turnos sin solapamientos). (Etapa: Implementación y Verificación)
- **api-turnos**: Skill propia del proyecto para trabajar en la API HTTP de turnos (`src/api/`): ciclo TDD de la API, contrato de errores 409/422/404, semántica de intervalos `[inicio, fin)`, uso exclusivo de datos ficticios y trampas ya conocidas. Ruta: `.opencode/skills/api-turnos/SKILL.md` (identificador derivado de la ruta: `api-turnos`; referencias: `.opencode/skills/api-turnos/references/gotchas.md` y `.opencode/skills/api-turnos/references/contrato-http.md`). Disparador: toda tarea que toque la API de turnos, Swagger, `/docs`, `/openapi.json`, el contrato HTTP de citas o los tests de FastAPI del repositorio, aunque no se nombre la skill. (Etapa: Implementación y Verificación)
