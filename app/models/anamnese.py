from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Anamnese:
    patient_id: int
    data: date
    queixa_principal: str = ""
    objetivo: str = ""
    historico_saude: str = ""
    medicamentos: str = ""
    alergias: str = ""
    habitos_alimentares: str = ""
    ingestao_agua: str = ""
    rotina: str = ""
    sono: str = ""
    atividade_fisica: str = ""
    funcionamento_intestinal: str = ""
    alcool: str = ""
    tabagismo: str = ""
    observacoes: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        from ..utils.converters import (
            coerce_date_or_none,
            coerce_datetime,
            coerce_int,
            coerce_string,
        )

        self.patient_id = coerce_int(self.patient_id) or 0
        self.data = coerce_date_or_none(self.data)

        str_fields = [
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
        ]
        for field_name in str_fields:
            setattr(self, field_name, coerce_string(getattr(self, field_name)))

        self.id = coerce_int(self.id)
        self.created_at = coerce_datetime(self.created_at)
        self.updated_at = coerce_datetime(self.updated_at)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "data": self.data.isoformat() if isinstance(self.data, date) else None,
            "queixa_principal": self.queixa_principal,
            "objetivo": self.objetivo,
            "historico_saude": self.historico_saude,
            "medicamentos": self.medicamentos,
            "alergias": self.alergias,
            "habitos_alimentares": self.habitos_alimentares,
            "ingestao_agua": self.ingestao_agua,
            "rotina": self.rotina,
            "sono": self.sono,
            "atividade_fisica": self.atividade_fisica,
            "funcionamento_intestinal": self.funcionamento_intestinal,
            "alcool": self.alcool,
            "tabagismo": self.tabagismo,
            "observacoes": self.observacoes,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else None,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else None,
        }
