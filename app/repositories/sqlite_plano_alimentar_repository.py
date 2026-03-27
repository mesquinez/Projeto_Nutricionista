import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from ..config import logger
from ..models.plano_alimentar import PlanoAlimentar
from .plano_alimentar_repository import PlanoAlimentarRepository


class SQLitePlanoAlimentarRepository(PlanoAlimentarRepository):
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
                CREATE TABLE IF NOT EXISTS planos_alimentares (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    cafe_manha TEXT DEFAULT '',
                    lanche_manha TEXT DEFAULT '',
                    almoco TEXT DEFAULT '',
                    lanche_tarde TEXT DEFAULT '',
                    jantar TEXT DEFAULT '',
                    lanche_noite TEXT DEFAULT '',
                    observacoes TEXT DEFAULT '',
                    calorias INTEGER,
                    proteinas REAL,
                    carboidratos REAL,
                    gorduras REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def _row_to_plano(self, row: sqlite3.Row) -> PlanoAlimentar:
        return PlanoAlimentar(
            id=row["id"],
            patient_id=row["patient_id"],
            date=row["date"],
            cafe_manha=row["cafe_manha"],
            lanche_manha=row["lanche_manha"],
            almoco=row["almoco"],
            lanche_tarde=row["lanche_tarde"],
            jantar=row["jantar"],
            lanche_noite=row["lanche_noite"],
            observacoes=row["observacoes"],
            calorias=row["calorias"],
            proteinas=row["proteinas"],
            carboidratos=row["carboidratos"],
            gorduras=row["gorduras"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def add(self, plano: PlanoAlimentar) -> int:
        self._init_db()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO planos_alimentares (patient_id, date, cafe_manha, lanche_manha, almoco, lanche_tarde, jantar, lanche_noite, observacoes, calorias, proteinas, carboidratos, gorduras)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plano.patient_id,
                plano.date.isoformat(),
                plano.cafe_manha,
                plano.lanche_manha,
                plano.almoco,
                plano.lanche_tarde,
                plano.jantar,
                plano.lanche_noite,
                plano.observacoes,
                plano.calorias,
                plano.proteinas,
                plano.carboidratos,
                plano.gorduras,
            ))
            conn.commit()
            logger.info(f"Plano alimentar criado: Paciente={plano.patient_id}")
            return cursor.lastrowid or 0

    def update(self, plano: PlanoAlimentar) -> bool:
        if not plano.id:
            return False
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE planos_alimentares SET patient_id=?, date=?, cafe_manha=?, lanche_manha=?, 
                almoco=?, lanche_tarde=?, jantar=?, lanche_noite=?, observacoes=?, calorias=?, 
                proteinas=?, carboidratos=?, gorduras=?, updated_at=CURRENT_TIMESTAMP WHERE id=?
            """, (
                plano.patient_id,
                plano.date.isoformat(),
                plano.cafe_manha,
                plano.lanche_manha,
                plano.almoco,
                plano.lanche_tarde,
                plano.jantar,
                plano.lanche_noite,
                plano.observacoes,
                plano.calorias,
                plano.proteinas,
                plano.carboidratos,
                plano.gorduras,
                plano.id,
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, plano_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM planos_alimentares WHERE id=?", (plano_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_by_id(self, plano_id: int) -> Optional[PlanoAlimentar]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM planos_alimentares WHERE id=?", (plano_id,))
            row = cursor.fetchone()
            return self._row_to_plano(row) if row else None

    def get_by_patient(self, patient_id: int) -> List[PlanoAlimentar]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM planos_alimentares WHERE patient_id=? ORDER BY date DESC", (patient_id,))
            return [self._row_to_plano(row) for row in cursor.fetchall()]

    def get_last_by_patient(self, patient_id: int) -> Optional[PlanoAlimentar]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM planos_alimentares WHERE patient_id=? ORDER BY date DESC LIMIT 1", (patient_id,))
            row = cursor.fetchone()
            return self._row_to_plano(row) if row else None
