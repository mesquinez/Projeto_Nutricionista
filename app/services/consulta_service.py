from typing import List, Optional
from datetime import date
from ..config import logger
from ..models.consulta import Consulta
from ..utils.validation import ValidationResult, ValidationError


class ConsultaService:
    def __init__(self, repository):
        self.repository = repository

    def validate(self, consulta: Consulta) -> ValidationResult:
        errors: List[ValidationError] = []
        if not consulta.patient_id or consulta.patient_id <= 0:
            errors.append(ValidationError("patient_id", "Paciente não identificado ou inválido."))
            
        if not isinstance(consulta.date, date):
            errors.append(ValidationError("date", "A data da consulta fornecida é nula ou num formato gravemente inválido."))

        if consulta.proximo_retorno and isinstance(consulta.date, date):
            if consulta.proximo_retorno < consulta.date:
                errors.append(ValidationError("proximo_retorno", "A data do próximo retorno não pode ser anterior à data da consulta."))
                
        if consulta.peso_registrado is not None and consulta.peso_registrado < 0:
            errors.append(ValidationError("peso_registrado", "O peso registrado não pode ser negativo."))
            
        if not consulta.queixa_principal:
            errors.append(ValidationError("queixa_principal", "A queixa principal é um campo mínimo exigido."))
            
        return ValidationResult(success=len(errors) == 0, errors=errors)

    def create(self, consulta: Consulta) -> Consulta:
        result = self.validate(consulta)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))

        consulta_id = self.repository.add(consulta)
        consulta.id = consulta_id
        logger.info(f"Consulta criada ID={consulta.id} PATIENT={consulta.patient_id}")
        return consulta

    def update(self, consulta: Consulta) -> Consulta:
        if not consulta.id:
            raise ValueError("Impossível atualizar registro sem ID local.")

        errors = self.validate(consulta)
        if errors:
            raise ValueError(" ; ".join(errors))

        self.repository.update(consulta)
        logger.info(f"Consulta atualizada ID={consulta.id} PATIENT={consulta.patient_id}")
        return consulta

    def delete(self, consulta_id: int) -> bool:
        return self.repository.delete(consulta_id)

    def get_by_id(self, consulta_id: int) -> Optional[Consulta]:
        return self.repository.get_by_id(consulta_id)

    def get_by_patient(self, patient_id: int) -> List[Consulta]:
        return self.repository.get_by_patient(patient_id)

    def get_last(self, patient_id: int) -> Optional[Consulta]:
        return self.repository.get_last_by_patient(patient_id)
