from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional


@dataclass
class Consulta:
    patient_id: int
    date: date
    hora: Optional[time] = None
    
    queixa_principal: str = ""
    observacoes: str = ""
    conduta: str = ""
    proximo_retorno: Optional[date] = None
    peso_registrado: Optional[float] = None
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date': self.date.isoformat() if self.date else None,
            'hora': self.hora.isoformat() if self.hora else None,
            'queixa_principal': self.queixa_principal,
            'observacoes': self.observacoes,
            'conduta': self.conduta,
            'proximo_retorno': self.proximo_retorno.isoformat() if self.proximo_retorno else None,
            'peso_registrado': self.peso_registrado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
