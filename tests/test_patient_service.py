import pytest
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock

from app.models.patient import Patient
from app.services.patient_service import PatientService, ValidationResult
from app.repositories.patient_repository import PatientRepository
from app.controllers.patient_controller import PatientController


@pytest.fixture
def mock_repository():
    return Mock(spec=PatientRepository)


@pytest.fixture
def patient_service(mock_repository):
    return PatientService(repository=mock_repository)


@pytest.fixture
def patient_controller(patient_service):
    return PatientController(service=patient_service)


@pytest.fixture
def valid_patient():
    return Patient(
        id=1,
        name="João Silva",
        phone="(21)99700-9999",
        email="joao@email.com",
        birth_date=date(1990, 1, 15),
    )


class TestPatientServiceValidation:
    def test_valid_patient_passes_validation(self, patient_service, valid_patient):
        result = patient_service.validate(valid_patient)
        assert result.success is True
        assert len(result.errors) == 0

    def test_empty_name_fails_validation(self, patient_service):
        patient = Patient(
            id=1,
            name="",
            phone="(21)99700-9999",
            email="joao@email.com",
            birth_date=date(1990, 1, 15),
        )
        result = patient_service.validate(patient)
        assert result.success is False
        assert any(e.field == "name" for e in result.errors)

    def test_whitespace_name_fails_validation(self, patient_service):
        patient = Patient(
            id=1,
            name="   ",
            phone="(21)99700-9999",
            email="joao@email.com",
            birth_date=date(1990, 1, 15),
        )
        result = patient_service.validate(patient)
        assert result.success is False

    def test_invalid_phone_fails_validation(self, patient_service):
        patient = Patient(
            id=1,
            name="João Silva",
            phone="21997009999",
            email="joao@email.com",
            birth_date=date(1990, 1, 15),
        )
        result = patient_service.validate(patient)
        assert result.success is False
        assert any(e.field == "phone" for e in result.errors)

    def test_valid_phone_formats_pass(self, patient_service):
        valid_phones = [
            "(11)99999-9999",
            "(21)98765-4321",
            "(31)12345-6789",
        ]
        for phone in valid_phones:
            patient = Patient(
                id=1,
                name="João Silva",
                phone=phone,
                email="joao@email.com",
                birth_date=date(1990, 1, 15),
            )
            result = patient_service.validate(patient)
            assert result.success is True, f"Phone {phone} should be valid"

    def test_invalid_email_fails_validation(self, patient_service):
        patient = Patient(
            id=1,
            name="João Silva",
            phone="(21)99700-9999",
            email="email-invalido",
            birth_date=date(1990, 1, 15),
        )
        result = patient_service.validate(patient)
        assert result.success is False
        assert any(e.field == "email" for e in result.errors)

    def test_valid_email_formats_pass(self, patient_service):
        valid_emails = [
            "test@email.com",
            "user.name@domain.org",
            "user+tag@domain.co.uk",
        ]
        for email in valid_emails:
            patient = Patient(
                id=1,
                name="João Silva",
                phone="(21)99700-9999",
                email=email,
                birth_date=date(1990, 1, 15),
            )
            result = patient_service.validate(patient)
            assert result.success is True, f"Email {email} should be valid"

    def test_future_birth_date_fails_validation(self, patient_service):
        patient = Patient(
            id=1,
            name="João Silva",
            phone="(21)99700-9999",
            email="joao@email.com",
            birth_date=date.today() + timedelta(days=1),
        )
        result = patient_service.validate(patient)
        assert result.success is False
        assert any(e.field == "birth_date" for e in result.errors)

    def test_optional_fields_can_be_empty(self, patient_service):
        patient = Patient(
            id=1,
            name="João Silva",
            phone="",
            email="",
            birth_date=None,
        )
        result = patient_service.validate(patient)
        assert result.success is True


class TestPatientServiceCRUD:
    def test_create_patient_success(self, patient_service, mock_repository, valid_patient):
        mock_repository.add.return_value = 1

        result = patient_service.create(valid_patient)

        mock_repository.add.assert_called_once()
        assert result.id == 1

    def test_create_patient_validation_failure(self, patient_service, mock_repository):
        patient = Patient(
            id=1,
            name="",
            phone="",
            email="",
            birth_date=None,
        )

        with pytest.raises(ValueError) as exc_info:
            patient_service.create(patient)

        assert "nome é obrigatório" in str(exc_info.value)
        mock_repository.add.assert_not_called()

    def test_update_patient_success(self, patient_service, mock_repository, valid_patient):
        mock_repository.update.return_value = True

        result = patient_service.update(valid_patient)

        mock_repository.update.assert_called_once_with(valid_patient)

    def test_update_patient_without_id_fails(self, patient_service):
        patient = Patient(
            id=None,
            name="João Silva",
            phone="(21)99700-9999",
            email="joao@email.com",
            birth_date=date(1990, 1, 15),
        )

        with pytest.raises(ValueError) as exc_info:
            patient_service.update(patient)

        assert "sem ID" in str(exc_info.value)

    def test_delete_patient_success(self, patient_service, mock_repository):
        mock_repository.delete.return_value = True

        result = patient_service.delete(1)

        assert result is True
        mock_repository.delete.assert_called_once_with(1)

    def test_get_all_patients(self, patient_service, mock_repository, valid_patient):
        mock_repository.get_all.return_value = [valid_patient]

        result = patient_service.get_all()

        assert len(result) == 1
        mock_repository.get_all.assert_called_once()

    def test_get_patient_by_id(self, patient_service, mock_repository, valid_patient):
        mock_repository.get_by_id.return_value = valid_patient

        result = patient_service.get_by_id(1)

        assert result == valid_patient
        mock_repository.get_by_id.assert_called_once_with(1)

    def test_search_patients(self, patient_service, mock_repository, valid_patient):
        mock_repository.search.return_value = [valid_patient]

        result = patient_service.search("João")

        assert len(result) == 1
        mock_repository.search.assert_called_once_with("João")


class TestPatientController:
    def test_create_patient_delegates_to_service(self, patient_controller, mock_repository, valid_patient):
        mock_repository.add.return_value = 1

        result = patient_controller.create_patient(valid_patient)

        assert result.id == 1

    def test_search_with_empty_query_returns_all(self, patient_controller, mock_repository, valid_patient):
        mock_repository.get_all.return_value = [valid_patient]

        result = patient_controller.search_patients("")

        mock_repository.get_all.assert_called_once()
        assert len(result) == 1

    def test_search_with_whitespace_query_returns_all(self, patient_controller, mock_repository, valid_patient):
        mock_repository.get_all.return_value = [valid_patient]

        result = patient_controller.search_patients("   ")

        mock_repository.get_all.assert_called_once()


class TestPatientModel:
    def test_patient_to_dict(self, valid_patient):
        result = valid_patient.to_dict()

        assert result["id"] == 1
        assert result["name"] == "João Silva"
        assert result["phone"] == "(21)99700-9999"
        assert result["email"] == "joao@email.com"
        assert result["birth_date"] == "1990-01-15"

    def test_patient_to_dict_with_null_birth_date(self):
        patient = Patient(
            id=1,
            name="João Silva",
            phone="(21)99700-9999",
            email="joao@email.com",
            birth_date=None,
        )
        result = patient.to_dict()

        assert result["birth_date"] is None


class TestValidationResult:
    def test_error_messages_property(self):
        from app.services.patient_service import ValidationError

        result = ValidationResult(
            success=False,
            errors=[
                ValidationError("name", "Nome é obrigatório"),
                ValidationError("email", "Email inválido"),
            ],
        )

        assert len(result.error_messages) == 2
        assert "Nome é obrigatório" in result.error_messages
        assert "Email inválido" in result.error_messages
