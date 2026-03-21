from typing import List, Optional

from ..config import logger
from ..models.anamnese import Anamnese
from ..services.anamnese_service import AnamneseService


class AnamneseController:
    def __init__(self, service: AnamneseService):
        self.service = service

    def create_anamnese(self, anamnese: Anamnese) -> Anamnese:
        try:
            return self.service.create(anamnese)
        except ValueError as e:
            logger.warning(f"Erro ao criar anamnese: {e}")
            raise

    def update_anamnese(self, anamnese: Anamnese) -> Anamnese:
        try:
            return self.service.update(anamnese)
        except ValueError as e:
            logger.warning(f"Erro ao atualizar anamnese: {e}")
            raise

    def delete_anamnese(self, anamnese_id: int) -> bool:
        return self.service.delete(anamnese_id)

    def get_anamnese(self, anamnese_id: int) -> Optional[Anamnese]:
        return self.service.get_by_id(anamnese_id)

    def get_patient_anamnese(self, patient_id: int) -> Optional[Anamnese]:
        return self.service.get_by_patient(patient_id)

    def get_patient_anamnese_history(self, patient_id: int) -> List[Anamnese]:
        return self.service.get_history_by_patient(patient_id)

    def patient_has_anamnese(self, patient_id: int) -> bool:
        return self.service.has_anamnese(patient_id)
