from typing import List, Optional

from ..config import logger
from ..models.anamnese import Anamnese
from ..repositories.anamnese_repository import AnamneseRepository
from ..utils.validation import ValidationError, ValidationResult


class AnamneseService:
    def __init__(self, repository: AnamneseRepository):
        self.repository = repository

    def validate(self, anamnese: Anamnese) -> ValidationResult:
        errors: List[ValidationError] = []

        if not anamnese.patient_id or anamnese.patient_id <= 0:
            errors.append(ValidationError("patient_id", "Paciente não identificado."))

        if not anamnese.data:
            errors.append(ValidationError("data", "A data da anamnese é obrigatória."))

        if not anamnese.queixa_principal or not anamnese.queixa_principal.strip():
            errors.append(ValidationError("queixa_principal", "A queixa principal é obrigatória."))

        return ValidationResult(success=len(errors) == 0, errors=errors)

    def create(self, anamnese: Anamnese) -> Anamnese:
        result = self.validate(anamnese)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))

        anamnese_id = self.repository.add(anamnese)
        anamnese.id = anamnese_id
        logger.info(f"Anamnese criada com sucesso: ID={anamnese_id}")
        return anamnese

    def update(self, anamnese: Anamnese) -> Anamnese:
        if not anamnese.id:
            raise ValueError("Não é possível atualizar uma anamnese sem ID.")

        result = self.validate(anamnese)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))

        self.repository.update(anamnese)
        logger.info(f"Anamnese atualizada com sucesso: ID={anamnese.id}")
        return anamnese

    def delete(self, anamnese_id: int) -> bool:
        return self.repository.delete(anamnese_id)

    def get_by_id(self, anamnese_id: int) -> Optional[Anamnese]:
        return self.repository.get_by_id(anamnese_id)

    def get_by_patient(self, patient_id: int) -> Optional[Anamnese]:
        return self.repository.get_by_patient(patient_id)

    def get_history_by_patient(self, patient_id: int):
        return self.repository.get_by_patient_history(patient_id)

    def has_anamnese(self, patient_id: int) -> bool:
        return self.repository.get_by_patient(patient_id) is not None
