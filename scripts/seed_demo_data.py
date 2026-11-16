"""Prepara la base de demostracion de la API de turnos.

Crea, o verifica si ya existen, los recursos de demostracion con
identificadores conocidos: consultorio, profesional, sillon, paciente y
servicio. Todos los datos son ficticios.

El script nunca borra ni sobrescribe: si un registro ya existe, lo deja tal
como esta y lo informa. Eso permite ejecutarlo antes de cada demostracion sin
perdido el estado de las reservas creadas.

Uso:

    .venv\\Scripts\\python.exe scripts\\seed_demo_data.py
    .venv\\Scripts\\python.exe scripts\\seed_demo_data.py --database data/demo.sqlite3
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Callable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api.config import DEFAULT_DATABASE_PATH, ensure_parent_directory
from src.appointments import AppointmentRepository

DEMO_CLINIC_ID = "demo-clinic"
DEMO_PROFESSIONAL_ID = "demo-profesional"
DEMO_CHAIR_ID = "demo-sillon"
DEMO_PATIENT_ID = "demo-paciente"
DEMO_SERVICE_ID = "demo-consulta"
CLINIC_TIMEZONE = "America/Argentina/Buenos_Aires"


def _ensure(register: Callable[[], None]) -> bool:
    """Ejecuta el alta. Devuelve True si se creo y False si ya existia."""

    try:
        register()
    except sqlite3.IntegrityError:
        return False
    return True


def seed(database_path: Path) -> dict[str, bool]:
    """Crea o verifica los recursos de demostracion en la base indicada.

    Devuelve, por recurso, si fue creado en esta ejecucion.
    """

    ensure_parent_directory(database_path)
    repository = AppointmentRepository(database_path)

    return {
        "consultorio": _ensure(
            lambda: repository.register_clinic(
                DEMO_CLINIC_ID, CLINIC_TIMEZONE, manages_chairs=True
            )
        ),
        "profesional": _ensure(
            lambda: repository.register_professional(DEMO_CLINIC_ID, DEMO_PROFESSIONAL_ID)
        ),
        "sillon": _ensure(
            lambda: repository.register_chair(DEMO_CLINIC_ID, DEMO_CHAIR_ID)
        ),
        "paciente": _ensure(
            lambda: repository.register_patient(DEMO_CLINIC_ID, DEMO_PATIENT_ID)
        ),
        "servicio": _ensure(
            lambda: repository.register_service(DEMO_CLINIC_ID, DEMO_SERVICE_ID)
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepara los datos ficticios de demostracion de la API de turnos."
    )
    parser.add_argument(
        "--database",
        default=str(DEFAULT_DATABASE_PATH),
        help="Ruta de la base de datos a preparar (por defecto, la de la API).",
    )
    arguments = parser.parse_args(argv)

    database_path = Path(arguments.database)
    created = seed(database_path)

    print(f"Base de datos: {database_path}")
    print("Datos de demostracion (todos ficticios):")
    print(f"  consultorio : {DEMO_CLINIC_ID}")
    print(f"  profesional : {DEMO_PROFESSIONAL_ID}")
    print(f"  sillon      : {DEMO_CHAIR_ID}")
    print(f"  paciente    : {DEMO_PATIENT_ID}")
    print(f"  servicio    : {DEMO_SERVICE_ID}")
    print("Estado:")
    for resource, was_created in created.items():
        estado = "creado" if was_created else "ya existia (no se modifico)"
        print(f"  {resource:<12}: {estado}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
