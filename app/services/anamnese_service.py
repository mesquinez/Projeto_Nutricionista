from datetime import date
from typing import List, Optional

from ..config import logger
from ..models.anamnese import Anamnese
from ..repositories.anamnese_repository import AnamneseRepository


class AnamneseService:
    def __init__(self, repository: AnamneseRepository):
        self.repository = repository

    def create(self, anamnese: Anamnese) -> Anamnese:
        if not anamnese.patient_id:
            raise ValueError("patient_id é obrigatório")

        if not anamnese.date:
            anamnese.date = date.today()

        anamnese_id = self.repository.add(anamnese)
        anamnese.id = anamnese_id
        logger.info(f"Anamnese criada com sucesso: ID={anamnese_id}")
        return anamnese

    def update(self, anamnese: Anamnese) -> Anamnese:
        if not anamnese.id:
            raise ValueError("Não é possível atualizar uma anamnese sem ID.")

        self.repository.update(anamnese)
        logger.info(f"Anamnese atualizada com sucesso: ID={anamnese.id}")
        return anamnese

    def delete(self, anamnese_id: int) -> bool:
        return self.repository.delete(anamnese_id)

    def get_by_id(self, anamnese_id: int) -> Optional[Anamnese]:
        return self.repository.get_by_id(anamnese_id)

    def get_by_patient(self, patient_id: int) -> Optional[Anamnese]:
        return self.repository.get_by_patient(patient_id)

    def get_history_by_patient(self, patient_id: int) -> List[Anamnese]:
        return self.repository.get_by_patient_history(patient_id)

    def has_anamnese(self, patient_id: int) -> bool:
        anamnese = self.repository.get_by_patient(patient_id)
        return anamnese is not None
