# Proposal

## Why

El repositorio contiene un servicio de dominio SQLite probado, pero no una API ejecutable con la que el equipo pueda demostrar sus operaciones de agenda. Una interfaz HTTP local, documentada y probada permite validar el límite de integración sin esperar la configuración del consultorio, autenticación ni otros cambios del roadmap.

## What Changes

- Agregar una API HTTP ejecutable localmente con documentación interactiva en `/docs` y esquema OpenAPI en `/openapi.json`.
- Exponer solo las operaciones existentes: crear, consultar un turno por consultorio e ID, reprogramar y cancelar. No introducir listado, altas de recursos, cambios del dominio ni estados nuevos.
- Fijar el contrato de respuestas: crear responde `201` con el turno creado en el cuerpo; consultar, reprogramar y cancelar responden `200`, y la cancelación devuelve el turno ya cancelado para que el cliente vea el estado nuevo sin una segunda consulta. Cancelar conserva el registro, por lo que no es un `DELETE` ni un `204` sin cuerpo.
- Convertir el escenario de arranque y documentación en una prueba automatizada que inicia el comando documentado en loopback y verifica `/docs`, `/openapi.json` y las cuatro operaciones.
- Añadir pruebas HTTP para los cuatro endpoints, errores de validación/conflicto y aislamiento por consultorio. Declarar las dependencias en un manifiesto Python y validar la instalación y las pruebas en Python 3.14.
- Incorporar un script que prepare datos exclusivamente ficticios para la demostración, con IDs conocidos para consultorio, profesional, sillón, paciente y servicio; documentar los pasos de demo en `README.md`. El script no sobrescribe una base ya existente.
- Crear una skill propia de workspace para el ciclo de API de turnos, ubicada en `.opencode/skills/api-turnos/SKILL.md` (ubicación de skills de proyecto en OpenCode) y referenciada desde `AGENTS.md`. Crear la skill con la skill creadora `skill-creator` (skill global de OpenCode, `~/.config/opencode/skills/skill-creator/SKILL.md`) y documentar explícitamente ese creador.
- Configurar el servidor MCP Context7 para OpenCode en el archivo de configuración del proyecto `opencode.json` (raíz del repositorio), bajo `mcp.context7`, sin credenciales. Ese archivo no está cubierto por `.gitignore`, así que queda versionado junto con el resto de la configuración compartida. Usar el MCP durante el cambio para consultar la documentación pública vigente de las dependencias. El MCP no forma parte del runtime ni es requisito para ejecutar la suite.
- Mantener la API restringida a loopback y a datos ficticios; no considerarla apta para Internet, operación clínica ni datos reales.

### Rutas de OpenCode confirmadas

Verificadas contra la documentación oficial de OpenCode (`opencode.ai/docs/mcp`, `opencode.ai/docs/skills`) y contra la instalación local (OpenCode 1.19.5):

| Elemento | Ruta | Fuente |
|---|---|---|
| Configuración MCP del proyecto | `opencode.json` en la raíz del repositorio, clave `mcp.<nombre>` | Doc oficial "MCP servers → Config" (esquema v1: `mcp: Record(String, Union[Local, Remote])`). La instalación local 1.19.5 acepta además la forma anidada `mcp.servers.<nombre>`, verificada el 2026-11-16 con un servidor de prueba |
| Configuración MCP global (equipo) | `~/.config/opencode/opencode.json` | Doc oficial "Config → Locations"; es la que usa `opencode mcp add` en 1.19.5 |
| Skill propia del proyecto | `.opencode/skills/<id>/SKILL.md` | Doc oficial "Skills → Create"; verificado con `opencode debug skill` |
| Skill creadora | `~/.config/opencode/skills/skill-creator/SKILL.md` | Skill global `skill-creator` instalada en OpenCode |

El identificador de una skill lo determina la ruta (kebab-case); el `name` del frontmatter es solo una etiqueta visible y el `description` es lo que dispara la carga automática.

### Evaluación del MCP propuesto

Se propone Context7 MCP, servidor remoto alojado en `https://mcp.context7.com/mcp`. La integración de OpenCode para servidores remotos expone las herramientas `resolve-library-id` y `query-docs`; su función es resolver una biblioteca y consultar su documentación versionada, no leer o modificar archivos del repositorio. La conexión usa OAuth y la configuración no contiene claves: las credenciales quedan fuera del repositorio.

Según la página oficial consultada el 10-11-2026, el plan Free cuesta USD 0 e incluye 1.000 llamadas mensuales; al agotar el cupo, las solicitudes se pausan hasta el siguiente mes, con 20 llamadas adicionales por día. La página publica el plan Pro a USD 10 por usuario/mes, pero no se requiere ni propone para C-10. El repositorio de Context7 publica licencia MIT para su software; esto no modifica el costo ni las condiciones del servicio alojado. Fuentes: [Context7 en OpenCode](https://opencode.ai/docs/mcp/), [planes y precios de Context7](https://context7.com/docs/plans-pricing), [licencia del servidor](https://github.com/upstash/context7/blob/master/LICENSE), [skills en OpenCode](https://opencode.ai/docs/skills/).

En esta máquina el servidor Context7 ya está conectado en la configuración global y responde; la contribución de C-10 es dejar la conexión **declarada y versionada en el proyecto**, para que cualquiera que clone el repositorio pueda reproducir el uso.

### Consulta al MCP Context7 que fijó una decisión de este change

**Qué se pidió** (servidor MCP Context7, remoto, sin credenciales):

```
resolve-library-id
  libraryName: FastAPI
  query: FastAPI response_model status_code 201 POST and OpenAPI responses documentation

query-docs
  libraryId: /websites/fastapi_tiangolo
  query: POST status_code 201 with response_model, and how to document extra error
         responses (409, 422) in the OpenAPI schema with responses parameter
```

**Qué devolvió** (extracto literal de la documentación oficial devuelta por el MCP):

- *Path Operation Configuration*: `status_code=status.HTTP_201_CREATED` — "The status code is used in the
  response **and added to the OpenAPI schema**".
- *Additional Responses in OpenAPI*: `responses` — "Each of those response `dict`s can have a key `model`,
  containing a Pydantic model, just like `response_model`. FastAPI will take that model, generate its JSON
  Schema and include it in the correct place in OpenAPI."
- *Combining information*: `response_model`, `status_code` y `responses` "can be combined"; FastAPI "will keep
  the additional information from `responses`, and combine it with the JSON Schema from the model".

**Qué decisión del change cambió.** Antes de la consulta, la forma de declarar el contrato era
"handler en runtime + `response_model`", y los errores (409/422/404) solo existían en el código: el documento
OpenAPI mostraba el camino feliz y nada más. La consulta mostró que FastAPI tiene un mecanismo específico
para **declarar respuestas adicionales con su modelo dentro del documento**, y que el `status_code` también
se publica en el esquema. Eso fijó D5 y D6 tal como quedaron implementadas:

- `POST` de creación con `status_code=status.HTTP_201_CREATED` (publicado en el esquema, no solo devuelto).
- Los errores `409`, `422` y `404` declarados con `responses={...: {"model": ErrorResponse, "description": ...}}`,
  de modo que `/openapi.json` describe el contrato completo y el cliente de Swagger puede ver los errores
  posibles sin leer el código.

El requisito del spec "el documento de contrato describe las operaciones" se cumple con ese mecanismo, no con
un `description` written a mano.

### Escenarios verificables propuestos

1. Una prueba automatizada inicia la aplicación mediante el comando documentado, limitado a `127.0.0.1`, y verifica que `/docs` responde y que `/openapi.json` lista crear, consultar por ID, reprogramar y cancelar.
2. Crear un turno en un consultorio con los recursos de demo devuelve el turno creado; consultarlo bajo ese consultorio devuelve los mismos datos operativos.
3. Reprogramar un turno disponible actualiza su intervalo; un conflicto devuelve `409` y un intervalo inválido devuelve `422`, sin modificar la reserva original ni exponer datos del paciente relacionado.
4. Cancelar un turno conserva el registro con estado cancelado; una nueva reserva puede reutilizar sus recursos.
5. Consultar un identificador inexistente o ajeno al consultorio indicado devuelve un error no revelador y no filtra datos de otro consultorio.
6. El script crea o verifica, sin borrado ni sobrescritura, una base de demostración con IDs documentados para consultorio, profesional, sillón, paciente y servicio; las dependencias se instalan y la suite se ejecuta en Python 3.14.
7. La skill propia se crea con `skill-creator`, queda en `.opencode/skills/api-turnos/SKILL.md`, es descubierta por OpenCode y se referencia desde `AGENTS.md` para que el agente la use en el ciclo de la API de turnos.
8. Context7 permite resolver FastAPI y consultar documentación pública relevante desde la configuración MCP del proyecto; una indisponibilidad o falta de cuota del MCP no bloquea la API ni sus pruebas.

## Capabilities

### New Capabilities

- `appointment-api`: contrato HTTP local para crear, consultar, reprogramar y cancelar turnos del servicio de dominio existente, incluido el descubrimiento OpenAPI.

### Modified Capabilities

Ninguna. C-10 no cambia los requisitos de dominio ya establecidos en `agenda-turnos`.

## Impact

- **Código previsto:** adaptador HTTP, esquemas de request/response, configuración de base de datos para la API, pruebas de integración y script de demo; el servicio SQLite de C-05 se consume sin reescribirlo.
- **Documentación/instrucciones previstas:** `README.md`, `AGENTS.md`, skill `.opencode/skills/api-turnos/SKILL.md`, configuración `opencode.json`, `TPI/evidencia-skill-mcp.md` y este roadmap.
- **Dependencias previstas:** FastAPI, Uvicorn y dependencias de prueba declaradas en el manifiesto Python; deben verificarse instalando en Python 3.14.
- **Dependencia funcional:** C-05 archivado. No depende de C-01–C-04 ni de C-06–C-09 y no los reemplaza.
- **Seguridad:** sin autenticación, autorizaciones por rol ni datos reales; escucha local únicamente. Context7 recibe consultas de documentación, no acceso al repositorio.
- **Estado:** propuesta OpenSpec para revisión del equipo. No se implementa en esta etapa.
