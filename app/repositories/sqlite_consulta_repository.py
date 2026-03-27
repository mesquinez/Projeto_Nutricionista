import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, time
from pathlib import Path
from typing import List, Optional

from ..config import logger
from ..models.consulta import Consulta
from .consulta_repository import ConsultaRepository


class SQLiteConsultaRepository(ConsultaRepository):
    def __init__(self, db_path: Path | str = "nutritionist.db"):
        self.db_path = Path(db_path)

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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    hora TEXT,
                    queixa_principal TEXT DEFAULT '',
                    observacoes TEXT DEFAULT '',
                    conduta TEXT DEFAULT '',
                    proximo_retorno TEXT,
                    peso_registrado REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def _row_to_consulta(self, row: sqlite3.Row) -> Consulta:
        return Consulta(
            id=row["id"],
            patient_id=row["patient_id"],
            date=row["date"],
            hora=row["hora"],
            queixa_principal=row["queixa_principal"],
            observacoes=row["observacoes"],
            conduta=row["conduta"],
            proximo_retorno=row["proximo_retorno"],
            peso_registrado=row["peso_registrado"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def add(self, consulta: Consulta) -> int:
        self._init_db()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO consultas (patient_id, date, hora, queixa_principal, observacoes, conduta, proximo_retorno, peso_registrado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                consulta.patient_id,
                consulta.date.isoformat(),
                consulta.hora.isoformat() if consulta.hora else None,
                consulta.queixa_principal,
                consulta.observacoes,
                consulta.conduta,
                consulta.proximo_retorno.isoformat() if consulta.proximo_retorno else None,
                consulta.peso_registrado,
            ))
            conn.commit()
            logger.info(f"Consulta criada: Paciente={consulta.patient_id}")
            return cursor.lastrowid or 0

    def update(self, consulta: Consulta) -> bool:
        if not consulta.id:
            return False
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE consultas SET patient_id=?, date=?, hora=?, queixa_principal=?, observacoes=?, 
                conduta=?, proximo_retorno=?, peso_registrado=?, updated_at=CURRENT_TIMESTAMP WHERE id=?
            """, (
                consulta.patient_id,
                consulta.date.isoformat(),
                consulta.hora.isoformat() if consulta.hora else None,
                consulta.queixa_principal,
                consulta.observacoes,
                consulta.conduta,
                consulta.proximo_retorno.isoformat() if consulta.proximo_retorno else None,
                consulta.peso_registrado,
                consulta.id,
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, consulta_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM consultas WHERE id=?", (consulta_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_by_id(self, consulta_id: int) -> Optional[Consulta]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM consultas WHERE id=?", (consulta_id,))
            row = cursor.fetchone()
            return self._row_to_consulta(row) if row else None

    def get_by_patient(self, patient_id: int) -> List[Consulta]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM consultas WHERE patient_id=? ORDER BY date DESC", (patient_id,))
            return [self._row_to_consulta(row) for row in cursor.fetchall()]

    def get_last_by_patient(self, patient_id: int) -> Optional[Consulta]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM consultas WHERE patient_id=? ORDER BY date DESC LIMIT 1", (patient_id,))
            row = cursor.fetchone()
            return self._row_to_consulta(row) if row else None
