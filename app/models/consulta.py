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

    def __post_init__(self):
        from ..utils.converters import (
            coerce_int, coerce_float, coerce_string, coerce_time,
            coerce_date_or_today, coerce_date_or_none, coerce_datetime
        )

        self.patient_id = coerce_int(self.patient_id) or 0
        self.date = coerce_date_or_today(self.date)
        self.hora = coerce_time(self.hora)
        self.queixa_principal = coerce_string(self.queixa_principal)
        self.observacoes = coerce_string(self.observacoes)
        self.conduta = coerce_string(self.conduta)
        self.proximo_retorno = coerce_date_or_none(self.proximo_retorno)
        self.peso_registrado = coerce_float(self.peso_registrado)
        self.id = coerce_int(self.id)
        self.created_at = coerce_datetime(self.created_at)
        self.updated_at = coerce_datetime(self.updated_at)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date': self.date.isoformat() if isinstance(self.date, date) else None,
            'hora': self.hora.isoformat() if isinstance(self.hora, time) else None,
            'queixa_principal': self.queixa_principal,
            'observacoes': self.observacoes,
            'conduta': self.conduta,
            'proximo_retorno': self.proximo_retorno.isoformat() if isinstance(self.proximo_retorno, date) else None,
            'peso_registrado': self.peso_registrado,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else None,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else None,
        }
