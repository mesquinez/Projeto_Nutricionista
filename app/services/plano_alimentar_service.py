from typing import List, Optional
from ..models.plano_alimentar import PlanoAlimentar


class PlanoAlimentarService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, plano: PlanoAlimentar) -> PlanoAlimentar:
        if not plano.patient_id:
            raise ValueError("patient_id é obrigatório")
        plano_id = self.repository.add(plano)
        plano.id = plano_id
        return plano

    def update(self, plano: PlanoAlimentar) -> PlanoAlimentar:
        if not plano.id:
            raise ValueError("ID é obrigatório")
        self.repository.update(plano)
        return plano

    def delete(self, plano_id: int) -> bool:
        return self.repository.delete(plano_id)

    def get_by_id(self, plano_id: int) -> Optional[PlanoAlimentar]:
        return self.repository.get_by_id(plano_id)

    def get_by_patient(self, patient_id: int) -> List[PlanoAlimentar]:
        return self.repository.get_by_patient(patient_id)

    def get_last(self, patient_id: int) -> Optional[PlanoAlimentar]:
        return self.repository.get_last_by_patient(patient_id)
