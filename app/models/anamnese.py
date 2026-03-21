from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Anamnese:
    patient_id: int
    date: date
    
    objetivo_principal: str = ""
    
    historico_peso: str = ""
    peso_maximo: Optional[float] = None
    peso_minimo: Optional[float] = None
    peso_desejado: Optional[float] = None
    
    atividade_fisica: str = ""
    frequencia_atividade: str = ""
    tempo_atividade: str = ""
    
    sono_qualidade: str = ""
    sono_horas: str = ""
    
    habitos_alimentares: str = ""
    refeicoes_dia: int = 0
    horarios_refeicoes: str = ""
    
    preferencia_alimentar: str = ""
    aversao_alimentar: str = ""
    alergio_intolerancias: str = ""
    
    consumo_agua: str = ""
    consumo_alcool: str = ""
    consumo_cigarro: str = ""
    
    doencas_previas: str = ""
    doencas_familiares: str = ""
    medicamentos: str = ""
    suplementacao: str = ""
    
    cirurgias: str = ""
    internacoes: str = ""
    
    ritmo_intestinal: str = ""
    observacoes_gerais: str = ""
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date': self.date.isoformat() if self.date else None,
            'objetivo_principal': self.objetivo_principal,
            'peso_maximo': self.peso_maximo,
            'peso_minimo': self.peso_minimo,
            'peso_desejado': self.peso_desejado,
            'atividade_fisica': self.atividade_fisica,
            'frequencia_atividade': self.frequencia_atividade,
            'tempo_atividade': self.tempo_atividade,
            'sono_qualidade': self.sono_qualidade,
            'sono_horas': self.sono_horas,
            'habitos_alimentares': self.habitos_alimentares,
            'refeicoes_dia': self.refeicoes_dia,
            'horarios_refeicoes': self.horarios_refeicoes,
            'preferencia_alimentar': self.preferencia_alimentar,
            'aversao_alimentar': self.aversao_alimentar,
            'alergio_intolerancias': self.alergio_intolerancias,
            'consumo_agua': self.consumo_agua,
            'consumo_alcool': self.consumo_alcool,
            'consumo_cigarro': self.consumo_cigarro,
            'doencas_previas': self.doencas_previas,
            'doencas_familiares': self.doencas_familiares,
            'medicamentos': self.medicamentos,
            'suplementacao': self.suplementacao,
            'cirurgias': self.cirurgias,
            'internacoes': self.internacoes,
            'ritmo_intestinal': self.ritmo_intestinal,
            'observacoes_gerais': self.observacoes_gerais,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
