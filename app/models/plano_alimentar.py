from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class PlanoAlimentar:
    patient_id: int
    date: date
    
    cafe_manha: str = ""
    lanche_manha: str = ""
    almoco: str = ""
    lanche_tarde: str = ""
    jantar: str = ""
    lanche_noite: str = ""
    
    observacoes: str = ""
    calorias: Optional[int] = None
    proteinas: Optional[float] = None
    carboidratos: Optional[float] = None
    gorduras: Optional[float] = None
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        from ..utils.converters import (
            coerce_int, coerce_float, coerce_string,
            coerce_date_or_today, coerce_datetime
        )

        self.patient_id = coerce_int(self.patient_id) or 0
        self.date = coerce_date_or_today(self.date)

        for field_name in ["proteinas", "carboidratos", "gorduras"]:
            setattr(self, field_name, coerce_float(getattr(self, field_name)))
            
        self.calorias = coerce_int(self.calorias)

        str_fields = ["cafe_manha", "lanche_manha", "almoco", "lanche_tarde", 
                      "jantar", "lanche_noite", "observacoes"]
        for field_name in str_fields:
            setattr(self, field_name, coerce_string(getattr(self, field_name)))

        self.id = coerce_int(self.id)
        self.created_at = coerce_datetime(self.created_at)
        self.updated_at = coerce_datetime(self.updated_at)

    def calcular_calorias_totais(self) -> int:
        p = self.proteinas or 0
        c = self.carboidratos or 0
        g = self.gorduras or 0
        calc = int((p * 4) + (c * 4) + (g * 9))
        return calc if calc > 0 else (self.calorias or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date': self.date.isoformat() if isinstance(self.date, date) else None,
            'cafe_manha': self.cafe_manha,
            'lanche_manha': self.lanche_manha,
            'almoco': self.almoco,
            'lanche_tarde': self.lanche_tarde,
            'jantar': self.jantar,
            'lanche_noite': self.lanche_noite,
            'observacoes': self.observacoes,
            'calorias': self.calorias,
            'proteinas': self.proteinas,
            'carboidratos': self.carboidratos,
            'gorduras': self.gorduras,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else None,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else None,
        }
