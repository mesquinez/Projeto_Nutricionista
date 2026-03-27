from datetime import date
from typing import List, Optional

from ..config import logger
from ..models.anamnese import Anamnese
from ..repositories.anamnese_repository import AnamneseRepository
from ..utils.validation import ValidationResult, ValidationError


class AnamneseService:
    def __init__(self, repository: AnamneseRepository):
        self.repository = repository

    def validate(self, anamnese: Anamnese) -> ValidationResult:
        errors = []
        if not anamnese.patient_id or anamnese.patient_id <= 0:
            errors.append(ValidationError("patient_id", "Paciente não identificado."))
            
        if not anamnese.objetivo_principal:
            errors.append(ValidationError("objetivo_principal", "O objetivo principal da anamnese é obrigatório."))

        if anamnese.peso_maximo is not None and anamnese.peso_maximo <= 0:
            errors.append(ValidationError("peso_maximo", "Peso máximo não pode ser negativo ou zero."))
        if anamnese.peso_minimo is not None and anamnese.peso_minimo <= 0:
            errors.append(ValidationError("peso_minimo", "Peso mínimo não pode ser negativo ou zero."))
        if anamnese.peso_desejado is not None and anamnese.peso_desejado <= 0:
            errors.append(ValidationError("peso_desejado", "Peso desejado não pode ser negativo ou zero."))

        if (anamnese.peso_maximo and anamnese.peso_minimo) and (anamnese.peso_minimo > anamnese.peso_maximo):
            errors.append(ValidationError("peso_minimo", "O peso mínimo informado é maior que o peso máximo."))

        return ValidationResult(success=len(errors) == 0, errors=errors)

    def create(self, anamnese: Anamnese) -> Anamnese:
        if not anamnese.date:
            anamnese.date = date.today()

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

        errors = self.validate(anamnese)
        if errors:
            raise ValueError(" ; ".join(errors))

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
