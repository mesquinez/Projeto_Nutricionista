from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class Avaliacao:
    patient_id: int
    date: date
    
    peso: Optional[float] = None
    altura: Optional[float] = None
    
    cintura: Optional[float] = None
    quadril: Optional[float] = None
    bracodireito: Optional[float] = None
    bracoesquedo: Optional[float] = None
    coxa: Optional[float] = None
    panturrilha: Optional[float] = None
    pescoco: Optional[float] = None
    
    dobra_triceps: Optional[float] = None
    dobra_biceps: Optional[float] = None
    dobra_subscapular: Optional[float] = None
    dobra_suprailiaca: Optional[float] = None
    dobra_abdominal: Optional[float] = None
    dobra_coxa: Optional[float] = None
    
    pressao_sistolica: Optional[int] = None
    pressao_diastolica: Optional[int] = None
    frequencia_cardiaca: Optional[int] = None
    
    observacoes: str = ""
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def calcular_imc(self) -> Optional[float]:
        if self.peso and self.altura and self.altura > 0:
            altura_m = self.altura / 100
            return round(self.peso / (altura_m ** 2), 2)
        return None

    def calcular_cintura_quadril(self) -> Optional[float]:
        if self.cintura and self.quadril and self.quadril > 0:
            return round(self.cintura / self.quadril, 2)
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date': self.date.isoformat() if self.date else None,
            'peso': self.peso,
            'altura': self.altura,
            'cintura': self.cintura,
            'quadril': self.quadril,
            'bracodireito': self.bracodireito,
            'bracoesquedo': self.bracoesquedo,
            'coxa': self.coxa,
            'panturrilha': self.panturrilha,
            'pescoco': self.pescoco,
            'dobra_triceps': self.dobra_triceps,
            'dobra_biceps': self.dobra_biceps,
            'dobra_subscapular': self.dobra_subscapular,
            'dobra_suprailiaca': self.dobra_suprailiaca,
            'dobra_abdominal': self.dobra_abdominal,
            'dobra_coxa': self.dobra_coxa,
            'pressao_sistolica': self.pressao_sistolica,
            'pressao_diastolica': self.pressao_diastolica,
            'frequencia_cardiaca': self.frequencia_cardiaca,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
