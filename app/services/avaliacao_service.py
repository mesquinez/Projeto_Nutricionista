from typing import List, Optional
from ..models.avaliacao import Avaliacao


class AvaliacaoService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, avaliacao: Avaliacao) -> Avaliacao:
        if not avaliacao.patient_id:
            raise ValueError("patient_id é obrigatório")
        avaliacao_id = self.repository.add(avaliacao)
        avaliacao.id = avaliacao_id
        return avaliacao

    def update(self, avaliacao: Avaliacao) -> Avaliacao:
        if not avaliacao.id:
            raise ValueError("ID é obrigatório")
        self.repository.update(avaliacao)
        return avaliacao

    def delete(self, avaliacao_id: int) -> bool:
        return self.repository.delete(avaliacao_id)

    def get_by_id(self, avaliacao_id: int) -> Optional[Avaliacao]:
        return self.repository.get_by_id(avaliacao_id)

    def get_by_patient(self, patient_id: int) -> List[Avaliacao]:
        return self.repository.get_by_patient(patient_id)

    def get_last(self, patient_id: int) -> Optional[Avaliacao]:
        return self.repository.get_last_by_patient(patient_id)

    def get_evolution_data(self, patient_id: int) -> List[dict]:
        avaliacoes = self.repository.get_by_patient(patient_id)
        return [
            {
                "date": a.date,
                "peso": a.peso,
                "altura": a.altura,
                "imc": a.calcular_imc(),
                "cintura_quadril": a.calcular_cintura_quadril(),
            }
            for a in avaliacoes if a.peso
        ]
