"""Inyeccion del repositorio de turnos en la API.

El repositorio se resuelve una vez por ruta de base de datos y se reutiliza.
Las pruebas sustituyen esta dependencia con ``app.dependency_overrides``.
"""

from __future__ import annotations

from src.api.config import ensure_parent_directory, resolve_database_path
from src.appointments import AppointmentRepository

_REPOSITORIES: dict[str, AppointmentRepository] = {}


def get_repository() -> AppointmentRepository:
    """Devuelve el repositorio de turnos asociado a la base configurada."""

    path = resolve_database_path()
    key = str(path.resolve())
    repository = _REPOSITORIES.get(key)
    if repository is None:
        ensure_parent_directory(path)
        repository = AppointmentRepository(path)
        _REPOSITORIES[key] = repository
    return repository


def clear_repository_cache() -> None:
    """Descarta los repositorios cacheados. Lo usan las pruebas."""

    _REPOSITORIES.clear()
