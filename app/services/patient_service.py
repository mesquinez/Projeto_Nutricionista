import re
from dataclasses import dataclass
from datetime import date
from typing import List

from ..config import logger
from ..models.patient import Patient
from ..repositories.patient_repository import PatientRepository


from ..config import logger
from ..models.patient import Patient
from ..repositories.patient_repository import PatientRepository
from ..utils.validation import ValidationResult, ValidationError


class PatientService:
    PHONE_PATTERN = re.compile(r"^\(\d{2}\)\s?\d{4,5}-\d{4}$")
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, repository: PatientRepository):
        self.repository = repository

    def validate(self, patient: Patient) -> ValidationResult:
        errors: List[ValidationError] = []

        # Nome completo é obrigatório
        if not patient.name or not patient.name.strip():
            errors.append(ValidationError("name", "O nome completo é obrigatório."))
        elif len(patient.name.strip().split()) < 2:
            errors.append(ValidationError("name", "Por favor, insira o nome completo."))

        # Telefone é obrigatório e deve ser válido
        if not patient.phone or not patient.phone.strip():
            errors.append(ValidationError("phone", "O telefone é obrigatório."))
        elif not self.PHONE_PATTERN.match(patient.phone):
            errors.append(
                ValidationError("phone", "Telefone inválido. Use o formato (21)99999-8888.")
            )

        # Data de nascimento é obrigatória e deve ser válida
        if not patient.birth_date:
            errors.append(ValidationError("birth_date", "A data de nascimento é obrigatória."))
        elif patient.birth_date > date.today():
            errors.append(ValidationError("birth_date", "A data de nascimento não pode ser futura."))
        elif patient.birth_date.year < 1900:
            errors.append(ValidationError("birth_date", "Data de nascimento inválida."))

        # E-mail é opcional, mas deve ser válido se preenchido
        if patient.email and patient.email.strip():
            if not self.EMAIL_PATTERN.match(patient.email):
                errors.append(ValidationError("email", "E-mail inválido."))

        # Telefone do responsável (se preenchido) deve ser válido
        if patient.guardian_phone and patient.guardian_phone.strip():
            if not self.PHONE_PATTERN.match(patient.guardian_phone):
                errors.append(
                    ValidationError("guardian_phone", "Telefone do responsável inválido. Use o formato (21)99999-8888.")
                )

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
