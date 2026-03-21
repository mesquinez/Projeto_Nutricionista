import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from ..config import logger
from ..models.anamnese import Anamnese
from .anamnese_repository import AnamneseRepository


class SQLiteAnamneseRepository(AnamneseRepository):
    COLUMNS = [
        "id", "patient_id", "date", "objetivo_principal",
        "peso_maximo", "peso_minimo", "peso_desejado",
        "atividade_fisica", "frequencia_atividade", "tempo_atividade",
        "sono_qualidade", "sono_horas",
        "habitos_alimentares", "refeicoes_dia", "horarios_refeicoes",
        "preferencia_alimentar", "aversao_alimentar", "alergio_intolerancias",
        "consumo_agua", "consumo_alcool", "consumo_cigarro",
        "doencas_previas", "doencas_familiares", "medicamentos", "suplementacao",
        "cirurgias", "internacoes", "ritmo_intestinal", "observacoes_gerais",
        "created_at", "updated_at"
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
                    date TEXT NOT NULL,
                    objetivo_principal TEXT DEFAULT '',
                    peso_maximo REAL,
                    peso_minimo REAL,
                    peso_desejado REAL,
                    atividade_fisica TEXT DEFAULT '',
                    frequencia_atividade TEXT DEFAULT '',
                    tempo_atividade TEXT DEFAULT '',
                    sono_qualidade TEXT DEFAULT '',
                    sono_horas TEXT DEFAULT '',
                    habitos_alimentares TEXT DEFAULT '',
                    refeicoes_dia INTEGER DEFAULT 0,
                    horarios_refeicoes TEXT DEFAULT '',
                    preferencia_alimentar TEXT DEFAULT '',
                    aversao_alimentar TEXT DEFAULT '',
                    alergio_intolerancias TEXT DEFAULT '',
                    consumo_agua TEXT DEFAULT '',
                    consumo_alcool TEXT DEFAULT '',
                    consumo_cigarro TEXT DEFAULT '',
                    doencas_previas TEXT DEFAULT '',
                    doencas_familiares TEXT DEFAULT '',
                    medicamentos TEXT DEFAULT '',
                    suplementacao TEXT DEFAULT '',
                    cirurgias TEXT DEFAULT '',
                    internacoes TEXT DEFAULT '',
                    ritmo_intestinal TEXT DEFAULT '',
                    observacoes_gerais TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
                )
                """
            )
            conn.commit()

    def _row_to_anamnese(self, row: sqlite3.Row) -> Anamnese:
        def parse_timestamp(value: Optional[str]) -> Optional[datetime]:
            if not value:
                return None
            return datetime.fromisoformat(value.replace(" ", "T"))

        return Anamnese(
            id=row["id"],
            patient_id=row["patient_id"],
            date=date.fromisoformat(row["date"]) if row["date"] else None,
            objetivo_principal=row["objetivo_principal"] or "",
            peso_maximo=row["peso_maximo"],
            peso_minimo=row["peso_minimo"],
            peso_desejado=row["peso_desejado"],
            atividade_fisica=row["atividade_fisica"] or "",
            frequencia_atividade=row["frequencia_atividade"] or "",
            tempo_atividade=row["tempo_atividade"] or "",
            sono_qualidade=row["sono_qualidade"] or "",
            sono_horas=row["sono_horas"] or "",
            habitos_alimentares=row["habitos_alimentares"] or "",
            refeicoes_dia=row["refeicoes_dia"] or 0,
            horarios_refeicoes=row["horarios_refeicoes"] or "",
            preferencia_alimentar=row["preferencia_alimentar"] or "",
            aversao_alimentar=row["aversao_alimentar"] or "",
            alergio_intolerancias=row["alergio_intolerancias"] or "",
            consumo_agua=row["consumo_agua"] or "",
            consumo_alcool=row["consumo_alcool"] or "",
            consumo_cigarro=row["consumo_cigarro"] or "",
            doencas_previas=row["doencas_previas"] or "",
            doencas_familiares=row["doencas_familiares"] or "",
            medicamentos=row["medicamentos"] or "",
            suplementacao=row["suplementacao"] or "",
            cirurgias=row["cirurgias"] or "",
            internacoes=row["internacoes"] or "",
            ritmo_intestinal=row["ritmo_intestinal"] or "",
            observacoes_gerais=row["observacoes_gerais"] or "",
            created_at=parse_timestamp(row["created_at"]),
            updated_at=parse_timestamp(row["updated_at"]),
        )

    def _get_fields(self, anamnese: Anamnese) -> dict:
        return {
            "patient_id": anamnese.patient_id,
            "date": anamnese.date.isoformat() if anamnese.date else None,
            "objetivo_principal": anamnese.objetivo_principal,
            "peso_maximo": anamnese.peso_maximo,
            "peso_minimo": anamnese.peso_minimo,
            "peso_desejado": anamnese.peso_desejado,
            "atividade_fisica": anamnese.atividade_fisica,
            "frequencia_atividade": anamnese.frequencia_atividade,
            "tempo_atividade": anamnese.tempo_atividade,
            "sono_qualidade": anamnese.sono_qualidade,
            "sono_horas": anamnese.sono_horas,
            "habitos_alimentares": anamnese.habitos_alimentares,
            "refeicoes_dia": anamnese.refeicoes_dia,
            "horarios_refeicoes": anamnese.horarios_refeicoes,
            "preferencia_alimentar": anamnese.preferencia_alimentar,
            "aversao_alimentar": anamnese.aversao_alimentar,
            "alergio_intolerancias": anamnese.alergio_intolerancias,
            "consumo_agua": anamnese.consumo_agua,
            "consumo_alcool": anamnese.consumo_alcool,
            "consumo_cigarro": anamnese.consumo_cigarro,
            "doencas_previas": anamnese.doencas_previas,
            "doencas_familiares": anamnese.doencas_familiares,
            "medicamentos": anamnese.medicamentos,
            "suplementacao": anamnese.suplementacao,
            "cirurgias": anamnese.cirurgias,
            "internacoes": anamnese.internacoes,
            "ritmo_intestinal": anamnese.ritmo_intestinal,
            "observacoes_gerais": anamnese.observacoes_gerais,
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
                "SELECT * FROM anamneses WHERE patient_id = ? ORDER BY date DESC LIMIT 1",
                (patient_id,)
            )
            row = cursor.fetchone()
            return self._row_to_anamnese(row) if row else None

    def get_by_patient_history(self, patient_id: int) -> List[Anamnese]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM anamneses WHERE patient_id = ? ORDER BY date DESC",
                (patient_id,)
            )
            rows = cursor.fetchall()
            return [self._row_to_anamnese(row) for row in rows]
