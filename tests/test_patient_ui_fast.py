import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import date

from app.services.patient_service import PatientService
from app.models.patient import Patient


class DummyRepo:
    def add(self, patient): return 1
    def update(self, patient): return True
    def delete(self, patient_id): return True
    def get_by_id(self, patient_id): return None
    def get_all(self): return []
    def search(self, query): return []


@pytest.fixture
def service():
    return PatientService(DummyRepo())


class TestValidationService:
    """Testa validações do service - execução instantânea"""

    def test_erro_sem_nome(self, service):
        patient = Patient(name="", phone="(21)99999-8888", birth_date=date(1990, 1, 1))
        result = service.validate(patient)
        assert not result.success
        assert any("nome" in e.message.lower() for e in result.errors)

    def test_erro_nome_apenas_uma_palavra(self, service):
        patient = Patient(name="Maria", phone="(21)99999-8888", birth_date=date(1990, 1, 1))
        result = service.validate(patient)
        assert not result.success
        assert any("nome" in e.message.lower() for e in result.errors)

    def test_erro_sem_telefone(self, service):
        patient = Patient(name="Maria Silva", phone="", birth_date=date(1990, 1, 1))
        result = service.validate(patient)
        assert not result.success
        assert any("telefone" in e.message.lower() for e in result.errors)

    def test_erro_telefone_formato_invalido(self, service):
        patient = Patient(name="Maria Silva", phone="21999998888", birth_date=date(1990, 1, 1))
        result = service.validate(patient)
        assert not result.success
        assert any("telefone" in e.message.lower() for e in result.errors)

    def test_erro_sem_data(self, service):
        patient = Patient(name="Maria Silva", phone="(21)99999-8888", birth_date=None)
        result = service.validate(patient)
        assert not result.success
        assert any("data" in e.message.lower() for e in result.errors)

    def test_erro_data_futura(self, service):
        patient = Patient(name="Maria Silva", phone="(21)99999-8888", birth_date=date(2030, 1, 1))
        result = service.validate(patient)
        assert not result.success
        assert any("data" in e.message.lower() for e in result.errors)

    def test_erro_data_antes_1900(self, service):
        patient = Patient(name="Maria Silva", phone="(21)99999-8888", birth_date=date(1800, 1, 1))
        result = service.validate(patient)
        assert not result.success
        assert any("data" in e.message.lower() for e in result.errors)

    def test_erro_email_invalido(self, service):
        patient = Patient(name="Maria Silva", phone="(21)99999-8888", birth_date=date(1990, 1, 1), email="email-invalido")
        result = service.validate(patient)
        assert not result.success
        assert any("e-mail" in e.message.lower() for e in result.errors)

    def test_sucesso_dados_validos(self, service):
        patient = Patient(name="Maria Silva", phone="(21)99999-8888", birth_date=date(1990, 1, 1))
        result = service.validate(patient)
        assert result.success
        assert len(result.errors) == 0

    def test_sucesso_com_dados_opcionais(self, service):
        patient = Patient(
            name="Maria Silva",
            phone="(21)99999-8888",
            birth_date=date(1990, 1, 1),
            email="maria@email.com",
            city="Rio de Janeiro",
            uf="RJ",
            profession="Médica"
        )
        result = service.validate(patient)
        assert result.success


class TestCreateUpdateService:
    """Testa create e update com validação integrada"""

    def test_create_erro_sem_nome(self, service):
        patient = Patient(name="", phone="(21)99999-8888", birth_date=date(1990, 1, 1))
        with pytest.raises(ValueError) as exc:
            service.create(patient)
        assert "nome" in str(exc.value).lower()

    def test_create_sucesso(self, service):
        patient = Patient(name="Maria Silva", phone="(21)99999-8888", birth_date=date(1990, 1, 1))
        result = service.create(patient)
        assert result.id == 1
        assert result.name == "Maria Silva"

    def test_update_erro_sem_id(self, service):
        patient = Patient(name="Maria Silva", phone="(21)99999-8888", birth_date=date(1990, 1, 1))
        with pytest.raises(ValueError) as exc:
            service.update(patient)
        assert "ID" in str(exc.value)

    def test_update_sucesso(self, service):
        patient = Patient(id=1, name="Maria Silva", phone="(21)99999-8888", birth_date=date(1990, 1, 1))
        result = service.update(patient)
        assert result.id == 1


class TestUIIntegration:
    """Testa integração UI -> Service simulando o fluxo completo"""

    def test_fluxo_cadastro_com_erros(self, service):
        """Simula o que acontece quando usuário clica salvar sem dados"""
        errors_captured = []

        def on_save(patient):
            result = service.validate(patient)
            if not result.success:
                errors_captured.extend(result.error_messages)
                return False
            service.create(patient)
            return True

        patient = Patient(name="", phone="", birth_date=None)
        on_save(patient)

        assert len(errors_captured) > 0
        error_text = " ".join(errors_captured).lower()
        assert "nome" in error_text or "telefone" in error_text or "data" in error_text

    def test_fluxo_cadastro_sucesso(self, service):
        """Simula o que acontece quando usuário preenche tudo certo"""
        saved_patients = []

        def on_save(patient):
            result = service.validate(patient)
            if not result.success:
                return False
            created = service.create(patient)
            saved_patients.append(created)
            return True

        patient = Patient(name="João Santos", phone="(21)99999-8888", birth_date=date(1985, 5, 15))
        success = on_save(patient)

        assert success is True
        assert len(saved_patients) == 1
        assert saved_patients[0].name == "João Santos"
