# Turnos Odontología

Sistema de gestión de turnos y agenda de pacientes para consultorios odontológicos, pensado para el mercado argentino.
Trabajo de integración de Metodología I (Spec-Driven Development con OpenSpec y Active Stack).

> **Estado:** prototipo de dominio. Hoy el repositorio contiene la investigación de mercado, la base de conocimiento, el roadmap y **un único change implementado y archivado**: *crear turnos sin solapamientos* (profesional y sillón). No hay interfaz ni API todavía.

## Requisitos

- Python 3.12 (versión con la que se corrieron las pruebas). No usa dependencias externas: solo la librería estándar (`sqlite3`, `datetime`, `unittest`).
- Git.

## Instalar y correr los tests

```bash
git clone https://github.com/Hondawave2545/Metodologia_1.git
cd Metodologia_1
python -m unittest discover -s tests -v
```

Resultado esperado: `Ran 18 tests ... OK`.

En Windows, si `python` no se reconoce, usar `py -m unittest discover -s tests -v`.

## Estructura

| Ruta | Contenido |
|---|---|
| `docs/discovery/` | Informe de Discovery (secciones A–D y verificación de fuentes) |
| `knowledge-base/` | Los 10 archivos canónicos del producto |
| `CHANGES.md` | Roadmap, dependencias y camino crítico |
| `AGENTS.md`, `CLAUDE.md` | Reglas para el agente de IA |
| `openspec/specs/` | Especificaciones vigentes |
| `openspec/changes/archive/` | Changes cerrados (proposal, design, tasks, specs) |
| `src/appointments.py` | Servicio de dominio de turnos (SQLite) |
| `tests/test_appointments.py` | Un test o más por cada escenario del spec |

## Datos y privacidad

Todos los ejemplos, pruebas y capturas usan datos ficticios. No se almacenan datos reales de pacientes ni credenciales en este repositorio.
