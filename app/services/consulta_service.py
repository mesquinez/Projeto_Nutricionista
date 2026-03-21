from typing import List, Optional
from ..models.consulta import Consulta


class ConsultaService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, consulta: Consulta) -> Consulta:
        if not consulta.patient_id:
            raise ValueError("patient_id é obrigatório")
        consulta_id = self.repository.add(consulta)
        consulta.id = consulta_id
        return consulta

    def update(self, consulta: Consulta) -> Consulta:
        if not consulta.id:
            raise ValueError("ID é obrigatório")
        self.repository.update(consulta)
        return consulta

    def delete(self, consulta_id: int) -> bool:
        return self.repository.delete(consulta_id)

    def get_by_id(self, consulta_id: int) -> Optional[Consulta]:
        return self.repository.get_by_id(consulta_id)

    def get_by_patient(self, patient_id: int) -> List[Consulta]:
        return self.repository.get_by_patient(patient_id)

    def get_last(self, patient_id: int) -> Optional[Consulta]:
        return self.repository.get_last_by_patient(patient_id)
