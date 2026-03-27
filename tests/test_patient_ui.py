import pytest
import tkinter as tk
from datetime import date
from unittest.mock import Mock, patch, MagicMock
import sys

from app.models.patient import Patient
from app.services.patient_service import PatientService
from app.repositories.patient_repository import PatientRepository


@pytest.fixture
def mock_repository():
    return Mock(spec=PatientRepository)


@pytest.fixture
def patient_service(mock_repository):
    return PatientService(repository=mock_repository)


class TestPatientServiceValidation:
    def test_erro_sem_nome(self, patient_service):
        patient = Patient(
            name="",
            phone="(21)99700-9999",
            birth_date=date(1990, 1, 15),
        )
        result = patient_service.validate(patient)
        assert result.success is False
        assert any(e.field == "name" for e in result.errors)

    def test_erro_sem_telefone(self, patient_service):
        patient = Patient(
            name="João Silva",
            phone="",
            birth_date=date(1990, 1, 15),
        )
        result = patient_service.validate(patient)
        assert result.success is False
        assert any(e.field == "phone" for e in result.errors)

    def test_erro_sem_data(self, patient_service):
        patient = Patient(
            name="João Silva",
            phone="(21)99700-9999",
            birth_date=None,
        )
        result = patient_service.validate(patient)
        assert result.success is False
        assert any(e.field == "birth_date" for e in result.errors)

    def test_erro_email_invalido(self, patient_service):
        patient = Patient(
            name="João Silva",
            phone="(21)99700-9999",
            birth_date=date(1990, 1, 15),
            email="email-invalido",
        )
        result = patient_service.validate(patient)
        assert result.success is False
        assert any(e.field == "email" for e in result.errors)

    def test_sucesso_dados_validos(self, patient_service):
        patient = Patient(
            name="João Silva",
            phone="(21)99700-9999",
            birth_date=date(1990, 1, 15),
            email="joao@email.com",
        )
        result = patient_service.validate(patient)
        assert result.success is True


class TestPatientWindowUI:
    @pytest.fixture
    def root(self):
        root = tk.Tk()
        root.withdraw()
        yield root
        try:
            root.destroy()
        except:
            pass

    @pytest.fixture
    def mock_on_save(self):
        return Mock(return_value=True)

    def test_erro_sem_nome_gera_mensagem(self, root, mock_on_save):
        with patch('app.ui.patient_window.messagebox') as mock_msgbox:
            from app.ui.patient_window import PatientFormWindow
            
            win = PatientFormWindow(root, on_save=mock_on_save)
            
            win.name_entry.insert(0, "")
            win.phone_entry.insert(0, "(21)99700-9999")
            if hasattr(win, 'birth_date_entry'):
                win.birth_date_entry.insert(0, "15/01/1990")
            elif hasattr(win, 'birth_date_picker'):
                win.birth_date_picker.set_date(date(1990, 1, 15))
            
            win._save()
            
            mock_msgbox.showerror.assert_called()
            mock_on_save.assert_not_called()

    def test_erro_sem_telefone_gera_mensagem(self, root, mock_on_save):
        with patch('app.ui.patient_window.messagebox') as mock_msgbox:
            from app.ui.patient_window import PatientFormWindow
            
            win = PatientFormWindow(root, on_save=mock_on_save)
            
            win.name_entry.insert(0, "João Silva")
            win.phone_entry.insert(0, "")
            if hasattr(win, 'birth_date_entry'):
                win.birth_date_entry.insert(0, "15/01/1990")
            elif hasattr(win, 'birth_date_picker'):
                win.birth_date_picker.set_date(date(1990, 1, 15))
            
            win._save()
            
            mock_msgbox.showerror.assert_called()
            mock_on_save.assert_not_called()

    def test_erro_sem_data_gera_mensagem(self, root, mock_on_save):
        with patch('app.ui.patient_window.messagebox') as mock_msgbox:
            from app.ui.patient_window import PatientFormWindow
            
            win = PatientFormWindow(root, on_save=mock_on_save)
            
            win.name_entry.insert(0, "João Silva")
            win.phone_entry.insert(0, "(21)99700-9999")
            
            win._save()
            
            mock_msgbox.showerror.assert_called()
            mock_on_save.assert_not_called()

    def test_sucesso_chama_on_save(self, root, mock_on_save, mock_repository):
        mock_repository.add.return_value = 1
        
        with patch('app.ui.patient_window.messagebox') as mock_msgbox:
            from app.ui.patient_window import PatientFormWindow
            
            win = PatientFormWindow(root, on_save=mock_on_save)
            
            win.name_entry.insert(0, "João Silva")
            win.phone_entry.insert(0, "(21)99700-9999")
            win.email_entry.insert(0, "joao@email.com")
            if hasattr(win, 'birth_date_entry'):
                win.birth_date_entry.insert(0, "15/01/1990")
            elif hasattr(win, 'birth_date_picker'):
                win.birth_date_picker.set_date(date(1990, 1, 15))
            
            win._save()
            
            mock_on_save.assert_called_once()
            assert mock_msgbox.showerror.call_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
