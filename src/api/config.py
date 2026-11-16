"""Configuracion de la API de turnos.

La ruta de la base de datos sale de la variable de entorno
``APPOINTMENTS_DB_PATH``. Sin esa variable se usa la base de demostracion del
proyecto, que solo contiene datos ficticios.
"""

from __future__ import annotations

import os
from pathlib import Path

ENVIRONMENT_VARIABLE = "APPOINTMENTS_DB_PATH"
DEFAULT_DATABASE_PATH = Path("data") / "demo.sqlite3"


def resolve_database_path() -> Path:
    """Devuelve la ruta de la base de datos configurada para la API."""

    configured = os.environ.get(ENVIRONMENT_VARIABLE)
    if configured:
        return Path(configured)
    return DEFAULT_DATABASE_PATH


def ensure_parent_directory(path: Path) -> None:
    """Crea el directorio contenedor de la base si todavia no existe."""

    path.parent.mkdir(parents=True, exist_ok=True)
