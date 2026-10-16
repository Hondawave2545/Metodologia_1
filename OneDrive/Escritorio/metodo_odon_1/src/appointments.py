"""Transactional appointment scheduling with professional and chair conflict checks."""

from __future__ import annotations

import sqlite3
import uuid
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


ACTIVE_STATUSES = ("scheduled", "confirmed")


class AppointmentError(Exception):
    """Base class for expected appointment domain errors."""


class InvalidAppointmentInterval(AppointmentError):
    """Raised when an appointment interval is invalid or timezone-naive."""


class AppointmentConflict(AppointmentError):
    """Raised when an appointment resource is already occupied."""

    def __init__(self, resource: str) -> None:
        self.resource = resource
        super().__init__(f"appointment_conflict:{resource}")


class ResourceUnavailable(AppointmentError):
    """Raised when a requested resource is missing, inactive, or out of scope."""


class ChairRequired(AppointmentError):
    """Raised when a clinic manages chairs but no chair was selected."""


class AppointmentNotFound(AppointmentError):
    """Raised when an appointment does not exist in the requested clinic."""


@dataclass(frozen=True)
class Appointment:
    id: str
    clinic_id: str
    professional_id: str
    chair_id: str | None
    patient_id: str
    service_id: str
    start_at: datetime
    end_at: datetime
    status: str


class AppointmentRepository:
    """SQLite-backed appointment storage with atomic resource conflict checks."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=10,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_database(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS clinics (
                    id TEXT PRIMARY KEY,
                    timezone TEXT NOT NULL,
                    manages_chairs INTEGER NOT NULL DEFAULT 0
                        CHECK (manages_chairs IN (0, 1))
                );

                CREATE TABLE IF NOT EXISTS professionals (
                    clinic_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
                    PRIMARY KEY (clinic_id, id),
                    FOREIGN KEY (clinic_id) REFERENCES clinics(id)
                );

                CREATE TABLE IF NOT EXISTS chairs (
                    clinic_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
                    PRIMARY KEY (clinic_id, id),
                    FOREIGN KEY (clinic_id) REFERENCES clinics(id)
                );

                CREATE TABLE IF NOT EXISTS patients (
                    clinic_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
                    PRIMARY KEY (clinic_id, id),
                    FOREIGN KEY (clinic_id) REFERENCES clinics(id)
                );

                CREATE TABLE IF NOT EXISTS services (
                    clinic_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
                    PRIMARY KEY (clinic_id, id),
                    FOREIGN KEY (clinic_id) REFERENCES clinics(id)
                );

                CREATE TABLE IF NOT EXISTS appointments (
                    id TEXT PRIMARY KEY,
                    clinic_id TEXT NOT NULL,
                    professional_id TEXT NOT NULL,
                    chair_id TEXT,
                    patient_id TEXT NOT NULL,
                    service_id TEXT NOT NULL,
                    start_at TEXT NOT NULL,
                    end_at TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('scheduled', 'confirmed', 'cancelled', 'completed', 'no_show')
                    ),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (clinic_id) REFERENCES clinics(id),
                    FOREIGN KEY (clinic_id, professional_id)
                        REFERENCES professionals(clinic_id, id),
                    FOREIGN KEY (clinic_id, chair_id)
                        REFERENCES chairs(clinic_id, id),
                    FOREIGN KEY (clinic_id, patient_id)
                        REFERENCES patients(clinic_id, id),
                    FOREIGN KEY (clinic_id, service_id)
                        REFERENCES services(clinic_id, id),
                    CHECK (start_at < end_at)
                );

                CREATE INDEX IF NOT EXISTS appointments_professional_interval
                    ON appointments(clinic_id, professional_id, status, start_at, end_at);
                CREATE INDEX IF NOT EXISTS appointments_chair_interval
                    ON appointments(clinic_id, chair_id, status, start_at, end_at);
                """
            )

    def register_clinic(
        self,
        clinic_id: str,
        timezone_name: str,
        *,
        manages_chairs: bool = False,
    ) -> None:
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO clinics (id, timezone, manages_chairs)
                VALUES (?, ?, ?)
                """,
                (clinic_id, timezone_name, int(manages_chairs)),
            )

    def register_professional(
        self, clinic_id: str, professional_id: str, *, active: bool = True
    ) -> None:
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO professionals (clinic_id, id, active) VALUES (?, ?, ?)",
                (clinic_id, professional_id, int(active)),
            )

    def register_chair(
        self, clinic_id: str, chair_id: str, *, active: bool = True
    ) -> None:
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO chairs (clinic_id, id, active) VALUES (?, ?, ?)",
                (clinic_id, chair_id, int(active)),
            )

    def register_patient(
        self, clinic_id: str, patient_id: str, *, active: bool = True
    ) -> None:
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO patients (clinic_id, id, active) VALUES (?, ?, ?)",
                (clinic_id, patient_id, int(active)),
            )

    def register_service(
        self, clinic_id: str, service_id: str, *, active: bool = True
    ) -> None:
        with self._transaction() as connection:
            connection.execute(
                "INSERT INTO services (clinic_id, id, active) VALUES (?, ?, ?)",
                (clinic_id, service_id, int(active)),
            )

    def create_appointment(
        self,
        *,
        clinic_id: str,
        professional_id: str,
        patient_id: str,
        service_id: str,
        start_at: datetime,
        end_at: datetime,
        chair_id: str | None = None,
    ) -> Appointment:
        start, end = _normalize_interval(start_at, end_at)
        appointment_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat(timespec="microseconds")

        with self._transaction() as connection:
            clinic = connection.execute(
                "SELECT manages_chairs FROM clinics WHERE id = ?",
                (clinic_id,),
            ).fetchone()
            if clinic is None:
                raise ResourceUnavailable("Clinic is unavailable")

            self._require_active_resource(
                connection, "professionals", clinic_id, professional_id
            )
            self._require_active_resource(connection, "patients", clinic_id, patient_id)
            self._require_active_resource(connection, "services", clinic_id, service_id)
            self._validate_chair(connection, clinic_id, clinic, chair_id)
            self._assert_no_conflict(
                connection,
                clinic_id=clinic_id,
                professional_id=professional_id,
                chair_id=chair_id,
                start_at=start,
                end_at=end,
            )

            connection.execute(
                """
                INSERT INTO appointments (
                    id, clinic_id, professional_id, chair_id, patient_id, service_id,
                    start_at, end_at, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'scheduled', ?, ?)
                """,
                (
                    appointment_id,
                    clinic_id,
                    professional_id,
                    chair_id,
                    patient_id,
                    service_id,
                    _serialize_datetime(start),
                    _serialize_datetime(end),
                    now,
                    now,
                ),
            )

        return Appointment(
            id=appointment_id,
            clinic_id=clinic_id,
            professional_id=professional_id,
            chair_id=chair_id,
            patient_id=patient_id,
            service_id=service_id,
            start_at=start,
            end_at=end,
            status="scheduled",
        )

    def reschedule_appointment(
        self,
        *,
        clinic_id: str,
        appointment_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> Appointment:
        start, end = _normalize_interval(start_at, end_at)

        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT * FROM appointments
                WHERE clinic_id = ? AND id = ?
                """,
                (clinic_id, appointment_id),
            ).fetchone()
            if row is None:
                raise AppointmentNotFound("Appointment not found")
            if row["status"] not in ACTIVE_STATUSES:
                raise ResourceUnavailable("Appointment is not active")

            self._assert_no_conflict(
                connection,
                clinic_id=clinic_id,
                professional_id=row["professional_id"],
                chair_id=row["chair_id"],
                start_at=start,
                end_at=end,
                exclude_appointment_id=appointment_id,
            )
            connection.execute(
                """
                UPDATE appointments
                SET start_at = ?, end_at = ?, updated_at = ?
                WHERE clinic_id = ? AND id = ?
                """,
                (
                    _serialize_datetime(start),
                    _serialize_datetime(end),
                    datetime.now(timezone.utc).isoformat(timespec="microseconds"),
                    clinic_id,
                    appointment_id,
                ),
            )
            updated = dict(row)
            updated["start_at"] = _serialize_datetime(start)
            updated["end_at"] = _serialize_datetime(end)

        return _appointment_from_row(updated)

    def cancel_appointment(self, *, clinic_id: str, appointment_id: str) -> None:
        with self._transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE appointments
                SET status = 'cancelled', updated_at = ?
                WHERE clinic_id = ? AND id = ? AND status IN ('scheduled', 'confirmed')
                """,
                (
                    datetime.now(timezone.utc).isoformat(timespec="microseconds"),
                    clinic_id,
                    appointment_id,
                ),
            )
            if cursor.rowcount == 0:
                raise AppointmentNotFound("Appointment not found")

    def get_appointment(
        self, *, clinic_id: str, appointment_id: str
    ) -> Appointment:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM appointments WHERE clinic_id = ? AND id = ?",
                (clinic_id, appointment_id),
            ).fetchone()
        if row is None:
            raise AppointmentNotFound("Appointment not found")
        return _appointment_from_row(row)

    def count_appointments(self, *, clinic_id: str) -> int:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM appointments WHERE clinic_id = ?",
                (clinic_id,),
            ).fetchone()
        return int(row["count"])

    @staticmethod
    def _require_active_resource(
        connection: sqlite3.Connection,
        table: str,
        clinic_id: str,
        resource_id: str,
    ) -> None:
        row = connection.execute(
            f"SELECT active FROM {table} WHERE clinic_id = ? AND id = ?",
            (clinic_id, resource_id),
        ).fetchone()
        if row is None or not row["active"]:
            raise ResourceUnavailable("Resource is unavailable")

    @classmethod
    def _validate_chair(
        cls,
        connection: sqlite3.Connection,
        clinic_id: str,
        clinic: sqlite3.Row,
        chair_id: str | None,
    ) -> None:
        if clinic["manages_chairs"] and chair_id is None:
            raise ChairRequired("A chair must be selected")
        if chair_id is not None:
            cls._require_active_resource(connection, "chairs", clinic_id, chair_id)

    @staticmethod
    def _assert_no_conflict(
        connection: sqlite3.Connection,
        *,
        clinic_id: str,
        professional_id: str,
        chair_id: str | None,
        start_at: datetime,
        end_at: datetime,
        exclude_appointment_id: str | None = None,
    ) -> None:
        exclusion = ""
        parameters: list[str] = [
            clinic_id,
            professional_id,
            _serialize_datetime(end_at),
            _serialize_datetime(start_at),
            *ACTIVE_STATUSES,
        ]
        if exclude_appointment_id is not None:
            exclusion = " AND id != ?"
            parameters.append(exclude_appointment_id)

        conflict = connection.execute(
            f"""
            SELECT 1 FROM appointments
            WHERE clinic_id = ?
                AND professional_id = ?
                AND start_at < ?
                AND end_at > ?
                AND status IN (?, ?)
                {exclusion}
            LIMIT 1
            """,
            parameters,
        ).fetchone()
        if conflict is not None:
            raise AppointmentConflict("professional")

        if chair_id is None:
            return

        parameters = [
            clinic_id,
            chair_id,
            _serialize_datetime(end_at),
            _serialize_datetime(start_at),
            *ACTIVE_STATUSES,
        ]
        if exclude_appointment_id is not None:
            parameters.append(exclude_appointment_id)
        conflict = connection.execute(
            f"""
            SELECT 1 FROM appointments
            WHERE clinic_id = ?
                AND chair_id = ?
                AND start_at < ?
                AND end_at > ?
                AND status IN (?, ?)
                {exclusion}
            LIMIT 1
            """,
            parameters,
        ).fetchone()
        if conflict is not None:
            raise AppointmentConflict("chair")


def _normalize_interval(start_at: datetime, end_at: datetime) -> tuple[datetime, datetime]:
    if start_at.tzinfo is None or start_at.utcoffset() is None:
        raise InvalidAppointmentInterval("start_at must include a timezone")
    if end_at.tzinfo is None or end_at.utcoffset() is None:
        raise InvalidAppointmentInterval("end_at must include a timezone")

    start = start_at.astimezone(timezone.utc)
    end = end_at.astimezone(timezone.utc)
    if start >= end:
        raise InvalidAppointmentInterval("start_at must be before end_at")
    return start, end


def _serialize_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _appointment_from_row(row: sqlite3.Row | dict[str, str]) -> Appointment:
    return Appointment(
        id=row["id"],
        clinic_id=row["clinic_id"],
        professional_id=row["professional_id"],
        chair_id=row["chair_id"],
        patient_id=row["patient_id"],
        service_id=row["service_id"],
        start_at=datetime.fromisoformat(row["start_at"]),
        end_at=datetime.fromisoformat(row["end_at"]),
        status=row["status"],
    )
