import csv
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional

from ..config import logger
from ..models.patient import Patient
from ..repositories.patient_repository import PatientRepository
from ..utils.validation import ValidationError, ValidationResult


@dataclass
class PatientImportError:
    line_number: int
    raw_data: dict
    reason: str


@dataclass
class PatientImportResult:
    success_count: int
    failure_count: int
    errors: List[PatientImportError]

    @property
    def total_processed(self) -> int:
        return self.success_count + self.failure_count


class PatientService:
    PHONE_PATTERN = re.compile(r"^\(\d{2}\)\s?\d{4,5}-\d{4}$")
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    REQUIRED_IMPORT_FIELDS = ("name", "birth_date", "phone")
    IMPORT_COLUMN_ALIASES = {
        "name": {
            "nome",
            "nome_completo",
            "nome completo",
            "nome do paciente",
            "paciente",
        },
        "birth_date": {
            "data_nascimento",
            "data nascimento",
            "data de nascimento",
            "nascimento",
            "birth_date",
        },
        "phone": {
            "telefone",
            "telefone principal",
            "celular",
            "fone",
            "phone",
        },
    }

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

    def import_from_csv(self, file_path: str | Path) -> PatientImportResult:
        path = Path(file_path)
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            sample = csv_file.read(2048)
            csv_file.seek(0)
            delimiter = self._detect_csv_delimiter(sample)
            reader = csv.DictReader(csv_file, delimiter=delimiter)

            if not reader.fieldnames:
                raise ValueError("A planilha estÃ¡ vazia ou sem cabeÃ§alho.")

            column_map = self._resolve_import_columns(reader.fieldnames)
            missing = [field for field in self.REQUIRED_IMPORT_FIELDS if field not in column_map]
            if missing:
                raise ValueError(
                    "Colunas obrigatÃ³rias ausentes: nome_completo, data_nascimento, telefone."
                )

            success_count = 0
            errors: List[PatientImportError] = []

            for line_number, row in enumerate(reader, start=2):
                if self._is_empty_row(row):
                    continue

                try:
                    patient = self._build_patient_from_import_row(row, column_map)
                    self.create(patient)
                    success_count += 1
                except ValueError as exc:
                    errors.append(
                        PatientImportError(
                            line_number=line_number,
                            raw_data=dict(row),
                            reason=str(exc),
                        )
                    )

        return PatientImportResult(
            success_count=success_count,
            failure_count=len(errors),
            errors=errors,
        )

    def _build_patient_from_import_row(self, row: dict, column_map: dict[str, str]) -> Patient:
        name = (row.get(column_map["name"]) or "").strip()
        phone = (row.get(column_map["phone"]) or "").strip()
        birth_date = self._parse_import_birth_date(row.get(column_map["birth_date"]))

        patient = Patient(
            name=name,
            phone=phone,
            birth_date=birth_date,
        )
        result = self.validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))
        return patient

    def _parse_import_birth_date(self, raw_value: Optional[str]) -> Optional[date]:
        value = (raw_value or "").strip()
        if not value:
            return None

        for separator in ("/", "-"):
            parts = value.split(separator)
            if len(parts) != 3:
                continue

            try:
                if len(parts[0]) == 4:
                    year, month, day = parts
                else:
                    day, month, year = parts
                return date(int(year), int(month), int(day))
            except ValueError:
                return None

        return None

    def _resolve_import_columns(self, fieldnames: List[str]) -> dict[str, str]:
        normalized_to_original = {
            self._normalize_import_column_name(fieldname): fieldname
            for fieldname in fieldnames
            if fieldname
        }

        resolved = {}
        for target_field, aliases in self.IMPORT_COLUMN_ALIASES.items():
            for alias in aliases:
                normalized_alias = self._normalize_import_column_name(alias)
                if normalized_alias in normalized_to_original:
                    resolved[target_field] = normalized_to_original[normalized_alias]
                    break

        return resolved

    def _normalize_import_column_name(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.strip().lower())
        ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9]+", "_", ascii_only).strip("_")

    def _is_empty_row(self, row: dict) -> bool:
        return all(not str(value or "").strip() for value in row.values())

    def _detect_csv_delimiter(self, sample: str) -> str:
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;")
            return dialect.delimiter
        except csv.Error:
            return ","
