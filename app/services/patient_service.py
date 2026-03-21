import re
from dataclasses import dataclass
from datetime import date
from typing import List

from ..config import logger
from ..models.patient import Patient
from ..repositories.patient_repository import PatientRepository


@dataclass
class ValidationError:
    field: str
    message: str


@dataclass
class ValidationResult:
    success: bool
    errors: List[ValidationError]

    @property
    def error_messages(self) -> List[str]:
        return [e.message for e in self.errors]


class PatientService:
    PHONE_PATTERN = re.compile(r"^\(\d{2}\)\d{5}-\d{4}$")
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, repository: PatientRepository):
        self.repository = repository

    def validate(self, patient: Patient) -> ValidationResult:
        errors: List[ValidationError] = []

        if not patient.name or not patient.name.strip():
            errors.append(ValidationError("name", "O nome é obrigatório."))

        if patient.phone:
            if not self.PHONE_PATTERN.match(patient.phone):
                errors.append(
                    ValidationError("phone", "Telefone inválido. Use o formato (21)99700-9999.")
                )

        if patient.email:
            if not self.EMAIL_PATTERN.match(patient.email):
                errors.append(ValidationError("email", "E-mail inválido."))

        if patient.birth_date:
            if patient.birth_date > date.today():
                errors.append(ValidationError("birth_date", "A data de nascimento não pode ser futura."))

        return ValidationResult(success=len(errors) == 0, errors=errors)

    def create(self, patient: Patient) -> Patient:
        result = self.validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))

        patient_id = self.repository.add(patient)
        patient.id = patient_id
        logger.info(f"Paciente criado com sucesso: ID={patient_id}, Nome={patient.name}")
        return patient

    def update(self, patient: Patient) -> Patient:
        if not patient.id:
            raise ValueError("Não é possível atualizar um paciente sem ID.")

        result = self.validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))

        self.repository.update(patient)
        logger.info(f"Paciente atualizado com sucesso: ID={patient.id}, Nome={patient.name}")
        return patient

    def delete(self, patient_id: int) -> bool:
        success = self.repository.delete(patient_id)
        if success:
            logger.info(f"Paciente excluído com sucesso: ID={patient_id}")
        return success

    def get_all(self) -> List[Patient]:
        return self.repository.get_all()

    def get_by_id(self, patient_id: int) -> Patient | None:
        return self.repository.get_by_id(patient_id)

    def search(self, query: str) -> List[Patient]:
        return self.repository.search(query)
