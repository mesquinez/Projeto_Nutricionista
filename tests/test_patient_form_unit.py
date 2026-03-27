"""
Testes de UI do formulário de pacientes - VERSÃO SEM Tkinter REAL
Usa mocks para garantir execução confiável em qualquer ambiente.
"""
import pytest
import tkinter as tk
from datetime import date
from unittest.mock import MagicMock, patch, PropertyMock
from app.models.patient import Patient
from app.services.patient_service import PatientService


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


@pytest.fixture
def mock_window():
    """Cria mock da janela com todos os campos necessários."""
    window = MagicMock()
    
    window.name_entry = MagicMock()
    window.name_entry.get = MagicMock(return_value="")
    window.name_entry.get.return_value = ""
    
    window.social_name_entry = MagicMock()
    window.social_name_entry.get = MagicMock(return_value="")
    
    window.phone_entry = MagicMock()
    window.phone_entry.get = MagicMock(return_value="")
    
    window.email_entry = MagicMock()
    window.email_entry.get = MagicMock(return_value="")
    
    window.city_entry = MagicMock()
    window.city_entry.get = MagicMock(return_value="")
    
    window.uf_entry = MagicMock()
    window.uf_entry.get = MagicMock(return_value="")
    
    window.profession_entry = MagicMock()
    window.profession_entry.get = MagicMock(return_value="")
    
    window.guardian_entry = MagicMock()
    window.guardian_entry.get = MagicMock(return_value="")
    
    window.guardian_phone_entry = MagicMock()
    window.guardian_phone_entry.get = MagicMock(return_value="")
    
    window.obs_text = MagicMock()
    window.obs_text.get = MagicMock(return_value="")
    
    window.status_var = MagicMock()
    window.status_var.get = MagicMock(return_value="Ativo")
    
    window.birth_date_entry = MagicMock()
    window.birth_date_entry.get = MagicMock(return_value="")
    
    window.birth_date_picker = MagicMock()
    window.birth_date_picker.get_date = MagicMock(return_value=None)
    
    return window


def get_field(window, field_name):
    """Retorna o campo correspondente ao nome."""
    fields = {
        "name": window.name_entry,
        "social_name": window.social_name_entry,
        "phone": window.phone_entry,
        "email": window.email_entry,
        "city": window.city_entry,
        "uf": window.uf_entry,
        "profession": window.profession_entry,
        "legal_guardian": window.guardian_entry,
        "guardian_phone": window.guardian_phone_entry,
        "birth_date": window.birth_date_entry,
    }
    return fields.get(field_name)


def set_field_value(window, field_name, value):
    """Define o valor de um campo."""
    field = get_field(window, field_name)
    if field:
        field.get.return_value = value


def make_patient_from_window(window):
    """Cria objeto Patient a partir dos valores da janela mockada."""
    from app.ui.patient_window import HAS_TKCALENDAR
    
    name = window.name_entry.get().strip()
    social_name = window.social_name_entry.get().strip()
    phone = window.phone_entry.get().strip()
    email = window.email_entry.get().strip()
    city = window.city_entry.get().strip()
    uf = window.uf_entry.get().upper().strip()
    profession = window.profession_entry.get().strip()
    legal_guardian = window.guardian_entry.get().strip()
    guardian_phone = window.guardian_phone_entry.get().strip()
    observations = window.obs_text.get("1.0", tk.END).strip() if hasattr(window.obs_text, 'get') else window.obs_text.get().strip()
    status = window.status_var.get()

    birth_date = None
    if HAS_TKCALENDAR:
        birth_date = window.birth_date_picker.get_date()
    else:
        birth_date_str = window.birth_date_entry.get().strip()
        if birth_date_str:
            try:
                day, month, year = birth_date_str.split("/")
                birth_date = date(int(year), int(month), int(day))
            except Exception:
                pass

    return Patient(
        id=None,
        name=name,
        social_name=social_name,
        phone=phone,
        email=email,
        birth_date=birth_date,
        city=city,
        uf=uf,
        profession=profession,
        legal_guardian=legal_guardian,
        guardian_phone=guardian_phone,
        observations=observations,
        status=status
    )


class TestValidationErrors:
    """Testes de validação - erros esperados."""

    def test_erro_sem_nome(self, service, mock_window):
        """Erro ao salvar sem nome."""
        set_field_value(mock_window, "name", "")
        set_field_value(mock_window, "phone", "(21)99999-8888")
        set_field_value(mock_window, "birth_date", "15/06/1990")
        
        patient = make_patient_from_window(mock_window)
        result = service.validate(patient)
        
        assert not result.success
        assert any("nome" in e.message.lower() for e in result.errors)

    def test_erro_nome_apenas_um_palavra(self, service, mock_window):
        """Erro ao salvar com apenas um palavra no nome."""
        set_field_value(mock_window, "name", "Maria")
        set_field_value(mock_window, "phone", "(21)99999-8888")
        set_field_value(mock_window, "birth_date", "15/06/1990")
        
        patient = make_patient_from_window(mock_window)
        result = service.validate(patient)
        
        assert not result.success
        assert any("nome" in e.message.lower() for e in result.errors)

    def test_erro_sem_telefone(self, service, mock_window):
        """Erro ao salvar sem telefone."""
        set_field_value(mock_window, "name", "Maria Silva")
        set_field_value(mock_window, "phone", "")
        set_field_value(mock_window, "birth_date", "15/06/1990")
        
        patient = make_patient_from_window(mock_window)
        result = service.validate(patient)
        
        assert not result.success
        assert any("telefone" in e.message.lower() for e in result.errors)

    def test_erro_telefone_formato_invalido(self, service, mock_window):
        """Erro ao salvar com telefone mal formatado."""
        set_field_value(mock_window, "name", "Maria Silva")
        set_field_value(mock_window, "phone", "2199999")
        set_field_value(mock_window, "birth_date", "15/06/1990")
        
        patient = make_patient_from_window(mock_window)
        result = service.validate(patient)
        
        assert not result.success
        assert any("telefone" in e.message.lower() for e in result.errors)

    def test_erro_sem_data_nascimento(self, service, mock_window):
        """Erro ao salvar sem data de nascimento."""
        set_field_value(mock_window, "name", "Maria Silva")
        set_field_value(mock_window, "phone", "(21)99999-8888")
        set_field_value(mock_window, "birth_date", "")
        
        with patch("app.ui.patient_window.HAS_TKCALENDAR", False):
            patient = make_patient_from_window(mock_window)
            result = service.validate(patient)
        
        assert not result.success
        assert any("data" in e.message.lower() for e in result.errors)

    def test_erro_data_futura(self, service, mock_window):
        """Erro ao salvar com data futura."""
        set_field_value(mock_window, "name", "Maria Silva")
        set_field_value(mock_window, "phone", "(21)99999-8888")
        set_field_value(mock_window, "birth_date", "15/06/2099")
        
        with patch("app.ui.patient_window.HAS_TKCALENDAR", False):
            patient = make_patient_from_window(mock_window)
            result = service.validate(patient)
        
        assert not result.success
        assert any("futura" in e.message.lower() for e in result.errors)

    def test_erro_data_muito_antiga(self, service, mock_window):
        """Erro ao salvar com data anterior a 1900."""
        set_field_value(mock_window, "name", "Maria Silva")
        set_field_value(mock_window, "phone", "(21)99999-8888")
        set_field_value(mock_window, "birth_date", "15/06/1800")
        
        with patch("app.ui.patient_window.HAS_TKCALENDAR", False):
            patient = make_patient_from_window(mock_window)
            result = service.validate(patient)
        
        assert not result.success
        assert any("data" in e.message.lower() for e in result.errors)

    def test_erro_email_invalido(self, service, mock_window):
        """Erro ao salvar com e-mail inválido."""
        set_field_value(mock_window, "name", "Maria Silva")
        set_field_value(mock_window, "phone", "(21)99999-8888")
        set_field_value(mock_window, "birth_date", "15/06/1990")
        set_field_value(mock_window, "email", "email-invalido")
        
        patient = make_patient_from_window(mock_window)
        result = service.validate(patient)
        
        assert not result.success
        assert any("e-mail" in e.message.lower() or "email" in e.message.lower() for e in result.errors)

    def test_erro_guardian_phone_invalido(self, service, mock_window):
        """Erro ao salvar com telefone do responsável inválido."""
        set_field_value(mock_window, "name", "Maria Silva")
        set_field_value(mock_window, "phone", "(21)99999-8888")
        set_field_value(mock_window, "birth_date", "15/06/1990")
        set_field_value(mock_window, "guardian_phone", "99999")
        
        patient = make_patient_from_window(mock_window)
        result = service.validate(patient)
        
        assert not result.success
        assert any("responsável" in e.message.lower() or "telefone" in e.message.lower() for e in result.errors)


class TestValidationSuccess:
    """Testes de validação - casos de sucesso."""

    def test_sucesso_dados_minimos(self, service, mock_window):
        """Sucesso com dados obrigatórios mínimos."""
        set_field_value(mock_window, "name", "Maria Silva")
        set_field_value(mock_window, "phone", "(21)99999-8888")
        set_field_value(mock_window, "birth_date", "15/06/1990")
        
        patient = make_patient_from_window(mock_window)
        result = service.validate(patient)
        
        assert result.success
        assert len(result.errors) == 0

    def test_sucesso_dados_completos(self, service, mock_window):
        """Sucesso com todos os dados preenchidos."""
        set_field_value(mock_window, "name", "Maria Silva Santos")
        set_field_value(mock_window, "phone", "(21)98765-4321")
        set_field_value(mock_window, "birth_date", "15/06/1990")
        set_field_value(mock_window, "email", "maria@email.com")
        set_field_value(mock_window, "city", "Rio de Janeiro")
        set_field_value(mock_window, "uf", "RJ")
        set_field_value(mock_window, "profession", "Médica")
        set_field_value(mock_window, "legal_guardian", "João Silva")
        set_field_value(mock_window, "guardian_phone", "(21)99999-0000")
        
        mock_window.obs_text.get = MagicMock(return_value="Observações do paciente")
        
        patient = make_patient_from_window(mock_window)
        result = service.validate(patient)
        
        assert result.success
        assert len(result.errors) == 0
        assert patient.name == "Maria Silva Santos"
        assert patient.email == "maria@email.com"
        assert patient.city == "Rio de Janeiro"

    def test_sucesso_campos_opcionais_vazios(self, service, mock_window):
        """Sucesso com campos opcionais vazios."""
        set_field_value(mock_window, "name", "João Pedro")
        set_field_value(mock_window, "phone", "(11)3333-4444")
        set_field_value(mock_window, "birth_date", "20/01/1985")
        
        patient = make_patient_from_window(mock_window)
        result = service.validate(patient)
        
        assert result.success
        assert patient.email is None or patient.email == ""
        assert patient.social_name is None or patient.social_name == ""


class TestPatientCreation:
    """Testes de criação de paciente."""

    def test_criar_paciente_valido(self, service, mock_window):
        """Cria paciente com dados válidos."""
        set_field_value(mock_window, "name", "Ana Carolina")
        set_field_value(mock_window, "phone", "(31)99999-1111")
        set_field_value(mock_window, "birth_date", "10/03/1995")
        
        patient = make_patient_from_window(mock_window)
        created = service.create(patient)
        
        assert created.id is not None
        assert created.name == "Ana Carolina"

    def test_criar_paciente_invalido_levanta_erro(self, service, mock_window):
        """Criação com dados inválidos levanta ValueError."""
        set_field_value(mock_window, "name", "")
        set_field_value(mock_window, "phone", "(31)99999-1111")
        set_field_value(mock_window, "birth_date", "10/03/1995")
        
        patient = make_patient_from_window(mock_window)
        
        with pytest.raises(ValueError) as exc_info:
            service.create(patient)
        
        assert "nome" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
