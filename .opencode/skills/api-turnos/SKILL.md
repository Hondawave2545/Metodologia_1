---
name: api-turnos
description: Trabajar en la API HTTP de turnos del sistema odontológico (src/api/): agregar o corregir endpoints, esquemas, mapeo de errores, pruebas de la API, script de datos de demostración o pruebas de arranque. Usar esta skill siempre que la tarea toque la API de turnos, Swagger, /docs, /openapi.json, el contrato HTTP de citas, o los tests de FastAPI del repositorio, aunque el usuario no la nombre por su nombre. Respetar el contrato de errores 409/422/404, la semántica de intervalos [inicio, fin) y el ciclo TDD del proyecto.
---

# API de turnos

Guía para trabajar en la capa HTTP del sistema de turnos. Reúne lo que la
implementación de C-10 (`src/api/`) ya estableció, para que otro agente no
tenga que redescubrirlo ni repetir los errores que ya costaron tiempo.

## Antes de tocar nada

1. Leé el spec del change: `openspec/changes/<change>/specs/appointment-api/spec.md`.
   Los escenarios son los criterios de aceptación; el código se escribe para
   satisfacerlos, no al revés.
2. Confirmá el estado real con el CLI, nunca de memoria:
   `openspec status --change "<change>" --json`.
3. Leé `AGENTS.md` y `CHANGES.md`. La semántica de agenda y la regla de datos
   ficticios están ahí y no se negocian.

## Reglas que no se negocian

- **El dominio es intocable.** `src/appointments.py` implementa la regla de
  negocio (solapamientos, estados que bloquean, aislamiento por consultorio) y
  está archivado y verificado. La API es un adaptador delgado: traduce
  requests a llamadas del dominio y errores del dominio a respuestas HTTP.
  Duplicar esa lógica en la capa HTTP crea dos fuentes de verdad para la regla
  más crítica del producto.
- **Intervalos semiabertos `[inicio, fin)`.** Solo `scheduled` y `confirmed`
  bloquean profesional y sillón. Cambiar esto exige un change aprobado.
- **Errores sin datos del paciente.** El cuerpo de error se construye con
  textos controlados (`DETAILS` en `src/api/errors.py`), nunca reenviando el
  mensaje de la excepción. Si alguna vez el cuerpo incluye texto libre, se
  puede filtrar identidad: es un bug, no una decisión de diseño.
- **Solo datos ficticios.** Los identificadores de demostración llevan el
  prefijo `demo-`. En el prototipo el paciente es un id opaco: no existe
  ninguna columna para nombre, documento o teléfono, así que los datos de
  demo no pueden contener información real.
- **Nada de autenticación, listados ni altas de recursos** en la API actual.
  No están en el alcance y no deben aparecer por convenience.

## Ciclo de trabajo

```
spec → test rojo → implementación mínima → test verde → suite completa → refactor
```

- Escribí el test primero, y verificá que falla por la razón que creés
  (import que no existe, o comportamiento que no está implementado).
- Después de cada grupo de trabajo, corré **la suite completa**. Si algo falla,
  no avances: primero determiná si el fallo es del código nuevo o una
  preexistencia.
- Una prueba que falla porque tu expectativa estaba mal **se corrige la
  expectativa**, pero solo cuando el código tiene razón. Si el código no
  cumple el spec, se corrige el código.
- Nunca debilites una aserción para que la prueba pase. Si una aserción era
  incorrecta (prohibía algo que el spec sí exige), reemplazala por una que
  cubra la misma intención de forma precisa, y dejá registrado el porqué.

## Verificación

```bash
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe -m unittest discover -s tests
```

Las dos deben coincidir. El suite completo incluye las pruebas del dominio
(`tests/test_appointments.py`), que **no deben modificarse**: si el cambio
las rompe, el problema está en el código nuevo.

Para levantar la API de verdad:

```bash
.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Una prueba que verifica el arranque real debe leer el comando del `README.md`
(marcadores `<!-- comando-de-arranque: inicio -->` / `fin`) y sustituir solo
intérprete y puerto. Así la documentación y la prueba no pueden divergir.

## Errores que ya se pagaron

Leé `references/gotchas.md` antes de escribir pruebas o levantar el servidor.
Los que más tiempo cuestan: el cliente de pruebas es `httpx2` y no `httpx`;
en Windows hay que cerrar las conexiones SQLite con `contextlib.closing`; y
`status.HTTP_422_UNPROCESSABLE_ENTITY` está deprecado.

## Contrato HTTP

Leé `references/contrato-http.md` para las rutas, los códigos de éxito y de
error, y el mapeo desde los errores del dominio. Es la referencia rápida; la
fuente normativa es el spec.

## Cuando terminés

- Actualizá `README.md` si cambiaron los comandos, las rutas o el contrato.
- Registrá la evidencia en `TPI/evidencia-skill-mcp.md` si usaste el MCP.
- Si el change quedó completo, verificá la suite y dejá el archivado para el
  paso explícito del proyecto: archivar sin que el equipo lo pida borra la
  posibilidad de revisar antes.
