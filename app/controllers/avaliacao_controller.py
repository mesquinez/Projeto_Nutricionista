from typing import List, Optional
from ..models.avaliacao import Avaliacao


class AvaliacaoController:
    def __init__(self, service):
        self.service = service

    def create(self, avaliacao: Avaliacao) -> Avaliacao:
        return self.service.create(avaliacao)

    def update(self, avaliacao: Avaliacao) -> Avaliacao:
        return self.service.update(avaliacao)

    def delete(self, avaliacao_id: int) -> bool:
        return self.service.delete(avaliacao_id)

    def get_by_id(self, avaliacao_id: int) -> Optional[Avaliacao]:
        return self.service.get_by_id(avaliacao_id)

    def get_by_patient(self, patient_id: int) -> List[Avaliacao]:
        return self.service.get_by_patient(patient_id)

    def get_last(self, patient_id: int) -> Optional[Avaliacao]:
        return self.service.get_last(patient_id)

    def get_evolution(self, patient_id: int) -> List[dict]:
        return self.service.get_evolution_data(patient_id)
