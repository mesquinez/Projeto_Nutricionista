import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from ..config import logger
from ..models.patient import Patient
from .patient_repository import PatientRepository


class SQLitePatientRepository(PatientRepository):
    COLUMNS = [
        "id", "name", "social_name", "phone", "email", "birth_date", 
        "city", "uf", "profession", "observations", 
        "legal_guardian", "guardian_phone", "status", "created_at", "updated_at"
    ]

    def __init__(self, db_path: Path | str = "nutritionist.db"):
        self.db_path = Path(db_path)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
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
                    social_name TEXT,
                    phone TEXT NOT NULL,
                    email TEXT,
                    birth_date TEXT NOT NULL,
                    city TEXT,
                    uf TEXT,
                    profession TEXT,
                    observations TEXT,
                    legal_guardian TEXT,
                    guardian_phone TEXT,
                    status TEXT DEFAULT 'Ativo',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
            self._migrate_schema(cursor)

    def _migrate_schema(self, cursor: sqlite3.Cursor):
        cursor.execute("PRAGMA table_info(patients)")
        columns = [row[1] for row in cursor.fetchall()]
        
        needed = [
            ("social_name", "TEXT"),
            ("city", "TEXT"),
            ("uf", "TEXT"),
            ("profession", "TEXT"),
            ("observations", "TEXT"),
            ("legal_guardian", "TEXT"),
            ("guardian_phone", "TEXT"),
            ("status", "TEXT DEFAULT 'Ativo'")
        ]
        
        for col_name, col_type in needed:
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE patients ADD COLUMN {col_name} {col_type}")
                logger.info(f"Coluna {col_name} adicionada à tabela patients")

    def add(self, patient: Patient) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO patients (
                    name, social_name, phone, email, birth_date, 
                    city, uf, profession, observations, 
                    legal_guardian, guardian_phone, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    patient.name,
                    patient.social_name,
                    patient.phone,
                    patient.email,
                    patient.birth_date.isoformat() if patient.birth_date else None,
                    patient.city,
                    patient.uf,
                    patient.profession,
                    patient.observations,
                    patient.legal_guardian,
                    patient.guardian_phone,
                    patient.status,
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
                SET name = ?, social_name = ?, phone = ?, email = ?, birth_date = ?, 
                    city = ?, uf = ?, profession = ?, observations = ?, 
                    legal_guardian = ?, guardian_phone = ?, status = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    patient.name,
                    patient.social_name,
                    patient.phone,
                    patient.email,
                    patient.birth_date.isoformat() if patient.birth_date else None,
                    patient.city,
                    patient.uf,
                    patient.profession,
                    patient.observations,
                    patient.legal_guardian,
                    patient.guardian_phone,
                    patient.status,
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
                WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR social_name LIKE ?
                ORDER BY name
                """,
                (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"),
            )
            rows = cursor.fetchall()
            return [self._row_to_patient(row) for row in rows]

    def _row_to_patient(self, row: sqlite3.Row) -> Patient:
        return Patient(
            id=row["id"],
            name=row["name"],
            social_name=row["social_name"],
            phone=row["phone"],
            email=row["email"],
            birth_date=row["birth_date"],
            city=row["city"],
            uf=row["uf"],
            profession=row["profession"],
            observations=row["observations"],
            legal_guardian=row["legal_guardian"],
            guardian_phone=row["guardian_phone"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
