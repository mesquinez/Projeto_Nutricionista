from typing import List, Optional
from ..models.plano_alimentar import PlanoAlimentar


class PlanoAlimentarController:
    def __init__(self, service):
        self.service = service

    def create(self, plano: PlanoAlimentar) -> PlanoAlimentar:
        return self.service.create(plano)

    def update(self, plano: PlanoAlimentar) -> PlanoAlimentar:
        return self.service.update(plano)

    def delete(self, plano_id: int) -> bool:
        return self.service.delete(plano_id)

    def get_by_id(self, plano_id: int) -> Optional[PlanoAlimentar]:
        return self.service.get_by_id(plano_id)

    def get_by_patient(self, patient_id: int) -> List[PlanoAlimentar]:
        return self.service.get_by_patient(patient_id)

    def get_last(self, patient_id: int) -> Optional[PlanoAlimentar]:
        return self.service.get_last(patient_id)
