import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from ..config import logger
from ..models.avaliacao import Avaliacao
from .avaliacao_repository import AvaliacaoRepository


class SQLiteAvaliacaoRepository(AvaliacaoRepository):
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
                CREATE TABLE IF NOT EXISTS avaliacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    peso REAL,
                    altura REAL,
                    cintura REAL,
                    quadril REAL,
                    bracodireito REAL,
                    bracoesquedo REAL,
                    coxa REAL,
                    panturrilha REAL,
                    pescoco REAL,
                    dobra_triceps REAL,
                    dobra_biceps REAL,
                    dobra_subscapular REAL,
                    dobra_suprailiaca REAL,
                    dobra_abdominal REAL,
                    dobra_coxa REAL,
                    pressao_sistolica INTEGER,
                    pressao_diastolica INTEGER,
                    frequencia_cardiaca INTEGER,
                    observacoes TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def _row_to_avaliacao(self, row: sqlite3.Row) -> Avaliacao:
        return Avaliacao(
            id=row["id"],
            patient_id=row["patient_id"],
            date=row["date"],
            peso=row["peso"],
            altura=row["altura"],
            cintura=row["cintura"],
            quadril=row["quadril"],
            bracodireito=row["bracodireito"],
            bracoesquedo=row["bracoesquedo"],
            coxa=row["coxa"],
            panturrilha=row["panturrilha"],
            pescoco=row["pescoco"],
            dobra_triceps=row["dobra_triceps"],
            dobra_biceps=row["dobra_biceps"],
            dobra_subscapular=row["dobra_subscapular"],
            dobra_suprailiaca=row["dobra_suprailiaca"],
            dobra_abdominal=row["dobra_abdominal"],
            dobra_coxa=row["dobra_coxa"],
            pressao_sistolica=row["pressao_sistolica"],
            pressao_diastolica=row["pressao_diastolica"],
            frequencia_cardiaca=row["frequencia_cardiaca"],
            observacoes=row["observacoes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def add(self, avaliacao: Avaliacao) -> int:
        self._init_db()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO avaliacoes (patient_id, date, peso, altura, cintura, quadril, bracodireito, bracoesquedo, coxa, panturrilha, pescoco, dobra_triceps, dobra_biceps, dobra_subscapular, dobra_suprailiaca, dobra_abdominal, dobra_coxa, pressao_sistolica, pressao_diastolica, frequencia_cardiaca, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                avaliacao.patient_id,
                avaliacao.date.isoformat(),
                avaliacao.peso,
                avaliacao.altura,
                avaliacao.cintura,
                avaliacao.quadril,
                avaliacao.bracodireito,
                avaliacao.bracoesquedo,
                avaliacao.coxa,
                avaliacao.panturrilha,
                avaliacao.pescoco,
                avaliacao.dobra_triceps,
                avaliacao.dobra_biceps,
                avaliacao.dobra_subscapular,
                avaliacao.dobra_suprailiaca,
                avaliacao.dobra_abdominal,
                avaliacao.dobra_coxa,
                avaliacao.pressao_sistolica,
                avaliacao.pressao_diastolica,
                avaliacao.frequencia_cardiaca,
                avaliacao.observacoes,
            ))
            conn.commit()
            logger.info(f"Avaliação criada: Paciente={avaliacao.patient_id}")
            return cursor.lastrowid or 0

    def update(self, avaliacao: Avaliacao) -> bool:
        if not avaliacao.id:
            return False
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE avaliacoes SET patient_id=?, date=?, peso=?, altura=?, cintura=?, quadril=?, 
                bracodireito=?, bracoesquedo=?, coxa=?, panturrilha=?, pescoco=?, dobra_triceps=?,
                dobra_biceps=?, dobra_subscapular=?, dobra_suprailiaca=?, dobra_abdominal=?, dobra_coxa=?,
                pressao_sistolica=?, pressao_diastolica=?, frequencia_cardiaca=?, observacoes=?,
                updated_at=CURRENT_TIMESTAMP WHERE id=?
            """, (
                avaliacao.patient_id,
                avaliacao.date.isoformat(),
                avaliacao.peso,
                avaliacao.altura,
                avaliacao.cintura,
                avaliacao.quadril,
                avaliacao.bracodireito,
                avaliacao.bracoesquedo,
                avaliacao.coxa,
                avaliacao.panturrilha,
                avaliacao.pescoco,
                avaliacao.dobra_triceps,
                avaliacao.dobra_biceps,
                avaliacao.dobra_subscapular,
                avaliacao.dobra_suprailiaca,
                avaliacao.dobra_abdominal,
                avaliacao.dobra_coxa,
                avaliacao.pressao_sistolica,
                avaliacao.pressao_diastolica,
                avaliacao.frequencia_cardiaca,
                avaliacao.observacoes,
                avaliacao.id,
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, avaliacao_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM avaliacoes WHERE id=?", (avaliacao_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_by_id(self, avaliacao_id: int) -> Optional[Avaliacao]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM avaliacoes WHERE id=?", (avaliacao_id,))
            row = cursor.fetchone()
            return self._row_to_avaliacao(row) if row else None

    def get_by_patient(self, patient_id: int) -> List[Avaliacao]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM avaliacoes WHERE patient_id=? ORDER BY date DESC", (patient_id,))
            return [self._row_to_avaliacao(row) for row in cursor.fetchall()]

    def get_last_by_patient(self, patient_id: int) -> Optional[Avaliacao]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM avaliacoes WHERE patient_id=? ORDER BY date DESC LIMIT 1", (patient_id,))
            row = cursor.fetchone()
            return self._row_to_avaliacao(row) if row else None
