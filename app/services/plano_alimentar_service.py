from typing import List, Optional
from datetime import date
from ..config import logger
from ..models.plano_alimentar import PlanoAlimentar
from ..utils.validation import ValidationResult, ValidationError


class PlanoAlimentarService:
    def __init__(self, repository):
        self.repository = repository

    def validate(self, plano: PlanoAlimentar) -> ValidationResult:
        errors = []
        if not plano.patient_id or plano.patient_id <= 0:
            errors.append(ValidationError("patient_id", "Paciente não identificado ou inválido."))
            
        if not isinstance(plano.date, date):
            errors.append(ValidationError("date", "A data do plano alimentar é inválida."))

        if plano.calorias is not None and plano.calorias < 0:
            errors.append(ValidationError("calorias", "As calorias não podem ser negativas."))
        if plano.proteinas is not None and plano.proteinas < 0:
            errors.append(ValidationError("proteinas", "Proteínas não podem ser negativas."))
        if plano.carboidratos is not None and plano.carboidratos < 0:
            errors.append(ValidationError("carboidratos", "Carboidratos não podem ser negativos."))
        if plano.gorduras is not None and plano.gorduras < 0:
            errors.append(ValidationError("gorduras", "Gorduras não podem ser negativas."))

        return ValidationResult(success=len(errors) == 0, errors=errors)

    def create(self, plano: PlanoAlimentar) -> PlanoAlimentar:
        result = self.validate(plano)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))

        plano_id = self.repository.add(plano)
        plano.id = plano_id
        logger.info(f"Plano criado ID={plano.id} PATIENT={plano.patient_id}")
        return plano

    def update(self, plano: PlanoAlimentar) -> PlanoAlimentar:
        if not plano.id:
            raise ValueError("Impossível atualizar plano sem ID local.")

        errors = self.validate(plano)
        if errors:
            raise ValueError(" ; ".join(errors))

        self.repository.update(plano)
        logger.info(f"Plano atualizado ID={plano.id} PATIENT={plano.patient_id}")
        return plano

    def delete(self, plano_id: int) -> bool:
        return self.repository.delete(plano_id)

    def get_by_id(self, plano_id: int) -> Optional[PlanoAlimentar]:
        return self.repository.get_by_id(plano_id)

    def get_by_patient(self, patient_id: int) -> List[PlanoAlimentar]:
        return self.repository.get_by_patient(patient_id)

    def get_last(self, patient_id: int) -> Optional[PlanoAlimentar]:
        return self.repository.get_last_by_patient(patient_id)
