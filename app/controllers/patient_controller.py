from typing import List, Optional

from ..config import logger
from ..models.patient import Patient
from ..services.patient_service import PatientService


class PatientController:
    def __init__(self, service: PatientService):
        self.service = service

    def create_patient(self, patient: Patient) -> Patient:
        try:
            return self.service.create(patient)
        except ValueError as e:
            logger.warning(f"Validação falhou ao criar paciente: {e}")
            raise

    def update_patient(self, patient: Patient) -> Patient:
        try:
            return self.service.update(patient)
        except ValueError as e:
            logger.warning(f"Validação falhou ao atualizar paciente: {e}")
            raise

    def delete_patient(self, patient_id: int) -> bool:
        return self.service.delete(patient_id)

    def get_all_patients(self) -> List[Patient]:
        return self.service.get_all()

    def get_patient(self, patient_id: int) -> Optional[Patient]:
        return self.service.get_by_id(patient_id)

    def search_patients(self, query: str) -> List[Patient]:
        if not query or not query.strip():
            return self.get_all_patients()
        return self.service.search(query)
