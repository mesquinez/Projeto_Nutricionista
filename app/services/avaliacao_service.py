from typing import List, Optional
from datetime import date
from ..config import logger
from ..models.avaliacao import Avaliacao
from ..utils.validation import ValidationResult, ValidationError


class AvaliacaoService:
    def __init__(self, repository):
        self.repository = repository

    def validate(self, avaliacao: Avaliacao) -> ValidationResult:
        errors = []
        if not avaliacao.patient_id or avaliacao.patient_id <= 0:
            errors.append(ValidationError("patient_id", "Paciente não identificado ou inválido."))
            
        if not isinstance(avaliacao.date, date):
            errors.append(ValidationError("date", "A data da avaliação é inválida."))

        if avaliacao.peso is not None and avaliacao.peso <= 0:
            errors.append(ValidationError("peso", "O peso deve ser maior que zero."))
            
        if avaliacao.altura is not None and avaliacao.altura <= 0:
            errors.append(ValidationError("altura", "A altura deve ser maior que zero (use centímetros)."))

        return ValidationResult(success=len(errors) == 0, errors=errors)

    def create(self, avaliacao: Avaliacao) -> Avaliacao:
        result = self.validate(avaliacao)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))

        avaliacao_id = self.repository.add(avaliacao)
        avaliacao.id = avaliacao_id
        logger.info(f"Avaliação criada ID={avaliacao.id} PATIENT={avaliacao.patient_id}")
        return avaliacao

    def update(self, avaliacao: Avaliacao) -> Avaliacao:
        if not avaliacao.id:
            raise ValueError("Impossível atualizar avaliação sem ID local.")

        errors = self.validate(avaliacao)
        if errors:
            raise ValueError(" ; ".join(errors))

        self.repository.update(avaliacao)
        logger.info(f"Avaliação atualizada ID={avaliacao.id} PATIENT={avaliacao.patient_id}")
        return avaliacao

    def delete(self, avaliacao_id: int) -> bool:
        return self.repository.delete(avaliacao_id)

    def get_by_id(self, avaliacao_id: int) -> Optional[Avaliacao]:
        return self.repository.get_by_id(avaliacao_id)

    def get_by_patient(self, patient_id: int) -> List[Avaliacao]:
        return self.repository.get_by_patient(patient_id)

    def get_last(self, patient_id: int) -> Optional[Avaliacao]:
        return self.repository.get_last_by_patient(patient_id)

    def get_evolution_data(self, patient_id: int) -> List[dict]:
        avaliacoes = self.repository.get_by_patient(patient_id)
        return [
            {
                "date": a.date,
                "peso": a.peso,
                "altura": a.altura,
                "imc": a.calcular_imc(),
                "cintura_quadril": a.calcular_cintura_quadril(),
            }
            for a in avaliacoes if a.peso
        ]
