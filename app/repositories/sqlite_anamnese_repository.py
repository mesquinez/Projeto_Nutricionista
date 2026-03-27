import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional

from ..config import logger
from ..models.anamnese import Anamnese
from .anamnese_repository import AnamneseRepository


class SQLiteAnamneseRepository(AnamneseRepository):
    COLUMNS = [
        "id",
        "patient_id",
        "data",
        "queixa_principal",
        "objetivo",
        "historico_saude",
        "medicamentos",
        "alergias",
        "habitos_alimentares",
        "ingestao_agua",
        "rotina",
        "sono",
        "atividade_fisica",
        "funcionamento_intestinal",
        "alcool",
        "tabagismo",
        "observacoes",
        "created_at",
        "updated_at",
    ]

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
                """
                CREATE TABLE IF NOT EXISTS anamneses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    queixa_principal TEXT DEFAULT '',
                    objetivo TEXT DEFAULT '',
                    historico_saude TEXT DEFAULT '',
                    medicamentos TEXT DEFAULT '',
                    alergias TEXT DEFAULT '',
                    habitos_alimentares TEXT DEFAULT '',
                    ingestao_agua TEXT DEFAULT '',
                    rotina TEXT DEFAULT '',
                    sono TEXT DEFAULT '',
                    atividade_fisica TEXT DEFAULT '',
                    funcionamento_intestinal TEXT DEFAULT '',
                    alcool TEXT DEFAULT '',
                    tabagismo TEXT DEFAULT '',
                    observacoes TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
                )
                """
            )
            self._migrate_schema(cursor)
            conn.commit()

    def _migrate_schema(self, cursor: sqlite3.Cursor):
        cursor.execute("PRAGMA table_info(anamneses)")
        columns = [row[1] for row in cursor.fetchall()]

        needed = [
            ("data", "TEXT"),
            ("queixa_principal", "TEXT DEFAULT ''"),
            ("objetivo", "TEXT DEFAULT ''"),
            ("historico_saude", "TEXT DEFAULT ''"),
            ("alergias", "TEXT DEFAULT ''"),
            ("ingestao_agua", "TEXT DEFAULT ''"),
            ("rotina", "TEXT DEFAULT ''"),
            ("sono", "TEXT DEFAULT ''"),
            ("funcionamento_intestinal", "TEXT DEFAULT ''"),
            ("alcool", "TEXT DEFAULT ''"),
            ("tabagismo", "TEXT DEFAULT ''"),
            ("observacoes", "TEXT DEFAULT ''"),
        ]

        for col_name, col_type in needed:
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE anamneses ADD COLUMN {col_name} {col_type}")
                logger.info(f"Coluna {col_name} adicionada à tabela anamneses")

        if "date" in columns:
            cursor.execute(
                """
                UPDATE anamneses
                SET data = COALESCE(data, date)
                WHERE data IS NULL OR data = ''
                """
            )

    def _row_to_anamnese(self, row: sqlite3.Row) -> Anamnese:
        return Anamnese(
            id=row["id"],
            patient_id=row["patient_id"],
            data=row["data"],
            queixa_principal=row["queixa_principal"],
            objetivo=row["objetivo"],
            historico_saude=row["historico_saude"],
            medicamentos=row["medicamentos"],
            alergias=row["alergias"],
            habitos_alimentares=row["habitos_alimentares"],
            ingestao_agua=row["ingestao_agua"],
            rotina=row["rotina"],
            sono=row["sono"],
            atividade_fisica=row["atividade_fisica"],
            funcionamento_intestinal=row["funcionamento_intestinal"],
            alcool=row["alcool"],
            tabagismo=row["tabagismo"],
            observacoes=row["observacoes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _get_fields(self, anamnese: Anamnese) -> dict:
        return {
            "patient_id": anamnese.patient_id,
            "data": anamnese.data.isoformat() if anamnese.data else None,
            "queixa_principal": anamnese.queixa_principal,
            "objetivo": anamnese.objetivo,
            "historico_saude": anamnese.historico_saude,
            "medicamentos": anamnese.medicamentos,
            "alergias": anamnese.alergias,
            "habitos_alimentares": anamnese.habitos_alimentares,
            "ingestao_agua": anamnese.ingestao_agua,
            "rotina": anamnese.rotina,
            "sono": anamnese.sono,
            "atividade_fisica": anamnese.atividade_fisica,
            "funcionamento_intestinal": anamnese.funcionamento_intestinal,
            "alcool": anamnese.alcool,
            "tabagismo": anamnese.tabagismo,
            "observacoes": anamnese.observacoes,
        }

    def add(self, anamnese: Anamnese) -> int:
        fields = self._get_fields(anamnese)
        placeholders = ", ".join(["?"] * len(fields))
        columns = ", ".join(fields.keys())

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO anamneses ({columns}) VALUES ({placeholders})",
                tuple(fields.values())
            )
            conn.commit()
            anamnese_id = cursor.lastrowid or 0
            logger.info(f"Anamnese criada: ID={anamnese_id}, Paciente={anamnese.patient_id}")
            return anamnese_id

    def update(self, anamnese: Anamnese) -> bool:
        if not anamnese.id:
            return False

        fields = self._get_fields(anamnese)
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        values = list(fields.values()) + [anamnese.id]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE anamneses SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                values
            )
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Anamnese atualizada: ID={anamnese.id}, Paciente={anamnese.patient_id}")
            return success

    def delete(self, anamnese_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM anamneses WHERE id = ?", (anamnese_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Anamnese excluída: ID={anamnese_id}")
            return success

    def get_by_id(self, anamnese_id: int) -> Optional[Anamnese]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM anamneses WHERE id = ?", (anamnese_id,))
            row = cursor.fetchone()
            return self._row_to_anamnese(row) if row else None

    def get_by_patient(self, patient_id: int) -> Optional[Anamnese]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM anamneses WHERE patient_id = ? ORDER BY data DESC, id DESC LIMIT 1",
                (patient_id,)
            )
            row = cursor.fetchone()
            return self._row_to_anamnese(row) if row else None

    def get_by_patient_history(self, patient_id: int) -> List[Anamnese]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM anamneses WHERE patient_id = ? ORDER BY data DESC, id DESC",
                (patient_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_anamnese(row) for row in rows]
