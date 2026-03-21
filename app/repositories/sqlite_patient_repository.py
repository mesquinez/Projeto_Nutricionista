import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from ..config import logger
from ..models.patient import Patient
from .patient_repository import PatientRepository


class SQLitePatientRepository(PatientRepository):
    COLUMNS = ["id", "name", "phone", "email", "birth_date", "created_at", "updated_at"]

    def __init__(self, db_path: Path | str = "nutritionist.db"):
        self.db_path = Path(db_path)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    birth_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
            self._migrate_legacy_columns(cursor)

    def _migrate_legacy_columns(self, cursor: sqlite3.Cursor):
        cursor.execute("PRAGMA table_info(patients)")
        columns = [row[1] for row in cursor.fetchall()]
        if "cpf" not in columns and "address" not in columns:
            return

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS patients_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                birth_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            f"""
            INSERT INTO patients_new ({", ".join(self.COLUMNS)})
            SELECT {", ".join(self.COLUMNS)} FROM patients
            """
        )
        cursor.execute("DROP TABLE patients")
        cursor.execute("ALTER TABLE patients_new RENAME TO patients")
        conn = cursor.connection
        conn.commit()
        logger.info("Migração de colunas legadas (cpf, address) concluída")

    def add(self, patient: Patient) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO patients (name, phone, email, birth_date)
                VALUES (?, ?, ?, ?)
                """,
                (
                    patient.name,
                    patient.phone,
                    patient.email,
                    patient.birth_date.isoformat() if patient.birth_date else None,
                ),
            )
            conn.commit()
            patient_id = cursor.lastrowid or 0
            logger.info(f"Paciente criado: ID={patient_id}, Nome={patient.name}")
            return patient_id

    def update(self, patient: Patient) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE patients
                SET name = ?, phone = ?, email = ?, birth_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    patient.name,
                    patient.phone,
                    patient.email,
                    patient.birth_date.isoformat() if patient.birth_date else None,
                    patient.id,
                ),
            )
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Paciente atualizado: ID={patient.id}, Nome={patient.name}")
            return success

    def delete(self, patient_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Paciente excluído: ID={patient_id}")
            return success

    def get_by_id(self, patient_id: int) -> Optional[Patient]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
            row = cursor.fetchone()
            return self._row_to_patient(row) if row else None

    def get_all(self) -> List[Patient]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients ORDER BY name")
            rows = cursor.fetchall()
            return [self._row_to_patient(row) for row in rows]

    def search(self, query: str) -> List[Patient]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM patients
                WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY name
                """,
                (f"%{query}%", f"%{query}%", f"%{query}%"),
            )
            rows = cursor.fetchall()
            return [self._row_to_patient(row) for row in rows]

    def _row_to_patient(self, row: sqlite3.Row) -> Patient:
        birth_str = row["birth_date"]
        birth_date_val: Optional[date] = date.fromisoformat(birth_str) if birth_str else None

        def parse_timestamp(value: Optional[str]) -> Optional[datetime]:
            if not value:
                return None
            return datetime.fromisoformat(value.replace(" ", "T"))

        return Patient(
            id=row["id"],
            name=row["name"],
            phone=row["phone"] or "",
            email=row["email"] or "",
            birth_date=birth_date_val,
            created_at=parse_timestamp(row["created_at"]),
            updated_at=parse_timestamp(row["updated_at"]),
        )
