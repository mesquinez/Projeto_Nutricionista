from typing import List, Optional
from ..models.consulta import Consulta


class ConsultaController:
    def __init__(self, service):
        self.service = service

    def create(self, consulta: Consulta) -> Consulta:
        return self.service.create(consulta)

    def update(self, consulta: Consulta) -> Consulta:
        return self.service.update(consulta)

    def delete(self, consulta_id: int) -> bool:
        return self.service.delete(consulta_id)

    def get_by_id(self, consulta_id: int) -> Optional[Consulta]:
        return self.service.get_by_id(consulta_id)

    def get_by_patient(self, patient_id: int) -> List[Consulta]:
        return self.service.get_by_patient(patient_id)

    def get_last(self, patient_id: int) -> Optional[Consulta]:
        return self.service.get_last(patient_id)
