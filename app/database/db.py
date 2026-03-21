import sqlite3
from datetime import date, datetime
from typing import Optional, List
from ..models.patient import Patient


class Database:
    def __init__(self, db_path: str = "nutritionist.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
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
            self._migrate_drop_cpf_and_address(cursor)

    def _migrate_drop_cpf_and_address(self, cursor: sqlite3.Cursor) -> None:
        """If legacy columns exist (cpf/address), rebuild table without them."""
        cursor.execute("PRAGMA table_info(patients)")
        columns = [row[1] for row in cursor.fetchall()]
        if "cpf" not in columns and "address" not in columns:
            return

        cursor.execute(
            """
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
            """
            INSERT INTO patients_new (id, name, phone, email, birth_date, created_at, updated_at)
            SELECT id, name, phone, email, birth_date, created_at, updated_at FROM patients
            """
        )
        cursor.execute("DROP TABLE patients")
        cursor.execute("ALTER TABLE patients_new RENAME TO patients")
        cursor.connection.commit()

    def add_patient(self, patient: Patient) -> int:
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
            return cursor.lastrowid or 0

    def update_patient(self, patient: Patient) -> bool:
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
            return cursor.rowcount > 0

    def delete_patient(self, patient_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_patient(self, patient_id: int) -> Optional[Patient]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_patient(row)
            return None

    def get_all_patients(self) -> List[Patient]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients ORDER BY name")
            rows = cursor.fetchall()
            return [self._row_to_patient(row) for row in rows]

    def search_patients(self, query: str) -> List[Patient]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
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
            # SQLite CURRENT_TIMESTAMP yields "YYYY-MM-DD HH:MM:SS"
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
