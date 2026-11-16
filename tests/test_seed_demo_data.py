"""Pruebas del script de datos ficticios de demostracion.

Verifican que el script prepara los recursos de demostracion con
identificadores conocidos, que no sobrescribe datos preexistentes y que no
introduce datos personales en el repositorio.
"""

import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.seed_demo_data import (
    DEMO_CHAIR_ID,
    DEMO_CLINIC_ID,
    DEMO_PATIENT_ID,
    DEMO_PROFESSIONAL_ID,
    DEMO_SERVICE_ID,
    seed,
)
from src.appointments import AppointmentRepository

PERSONAL_FIELD_MARKERS = (
    "nombre",
    "name",
    "apellido",
    "surname",
    "documento",
    "document",
    "dni",
    "telefono",
    "phone",
    "email",
    "mail",
    "direccion",
    "address",
    "nacimiento",
    "birth",
)


def _tables(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return [row[0] for row in rows]


def _columns(connection: sqlite3.Connection, table: str) -> list[str]:
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return [row[1] for row in rows]


class SeedDemoDataTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.database_path = Path(temporary_directory.name) / "demo.sqlite3"

    def test_creates_the_documented_demo_resources(self):
        created = seed(self.database_path)

        self.assertTrue(all(created.values()), created)
        with closing(sqlite3.connect(self.database_path)) as connection:
            self.assertIsNotNone(
                connection.execute(
                    "SELECT 1 FROM clinics WHERE id = ?", (DEMO_CLINIC_ID,)
                ).fetchone()
            )
            self.assertIsNotNone(
                connection.execute(
                    "SELECT 1 FROM professionals WHERE clinic_id = ? AND id = ?",
                    (DEMO_CLINIC_ID, DEMO_PROFESSIONAL_ID),
                ).fetchone()
            )
            self.assertIsNotNone(
                connection.execute(
                    "SELECT 1 FROM chairs WHERE clinic_id = ? AND id = ?",
                    (DEMO_CLINIC_ID, DEMO_CHAIR_ID),
                ).fetchone()
            )
            self.assertIsNotNone(
                connection.execute(
                    "SELECT 1 FROM patients WHERE clinic_id = ? AND id = ?",
                    (DEMO_CLINIC_ID, DEMO_PATIENT_ID),
                ).fetchone()
            )
            self.assertIsNotNone(
                connection.execute(
                    "SELECT 1 FROM services WHERE clinic_id = ? AND id = ?",
                    (DEMO_CLINIC_ID, DEMO_SERVICE_ID),
                ).fetchone()
            )

    def test_running_twice_preserves_the_existing_data(self):
        seed(self.database_path)

        second_run = seed(self.database_path)

        self.assertFalse(any(second_run.values()), second_run)
        with closing(sqlite3.connect(self.database_path)) as connection:
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM clinics WHERE id = ?", (DEMO_CLINIC_ID,)
                ).fetchone()[0],
            )
            self.assertEqual(
                1,
                connection.execute(
                    "SELECT COUNT(*) FROM patients WHERE clinic_id = ? AND id = ?",
                    (DEMO_CLINIC_ID, DEMO_PATIENT_ID),
                ).fetchone()[0],
            )

    def test_does_not_overwrite_a_preexisting_clinic_configuration(self):
        repository = AppointmentRepository(self.database_path)
        repository.register_clinic(
            DEMO_CLINIC_ID, "America/Argentina/Buenos_Aires", manages_chairs=False
        )

        seed(self.database_path)

        with closing(sqlite3.connect(self.database_path)) as connection:
            manages_chairs = connection.execute(
                "SELECT manages_chairs FROM clinics WHERE id = ?", (DEMO_CLINIC_ID,)
            ).fetchone()[0]
        self.assertEqual(
            0,
            manages_chairs,
            "El script no debe cambiar la configuracion de un consultorio preexistente.",
        )

    def test_demo_resources_use_fictional_identifiers(self):
        seed(self.database_path)

        for identifier in (
            DEMO_CLINIC_ID,
            DEMO_PROFESSIONAL_ID,
            DEMO_CHAIR_ID,
            DEMO_PATIENT_ID,
            DEMO_SERVICE_ID,
        ):
            self.assertTrue(identifier.startswith("demo-"), identifier)

    def test_the_database_has_no_field_to_store_personal_data(self):
        seed(self.database_path)

        with closing(sqlite3.connect(self.database_path)) as connection:
            columns = [
                column for table in _tables(connection) for column in _columns(connection, table)
            ]

        personal_fields = [
            column
            for column in columns
            if any(marker in column.lower() for marker in PERSONAL_FIELD_MARKERS)
        ]
        self.assertEqual([], personal_fields)


if __name__ == "__main__":
    unittest.main()
