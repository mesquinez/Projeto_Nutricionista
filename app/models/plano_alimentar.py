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

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date': self.date.isoformat() if self.date else None,
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
