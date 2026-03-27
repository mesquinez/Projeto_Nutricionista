import pytest
import tkinter as tk
from datetime import date

from app.ui.patient_window import PatientFormWindow
from app.services.patient_service import PatientService
from app.repositories.patient_repository import PatientRepository
from app.ui.utils.formatters import format_phone


class DummyRepo(PatientRepository):
    def add(self, patient): return 1
    def update(self, patient): return True
    def delete(self, patient_id): return True
    def get_by_id(self, patient_id): return None
    def get_all(self): return []
    def search(self, query): return []


_tk_root = None

def get_root():
    global _tk_root
    if _tk_root is None:
        _tk_root = tk.Tk()
        _tk_root.withdraw()
    return _tk_root


@pytest.fixture
def root():
    return get_root()


@pytest.fixture
def mock_messagebox(monkeypatch):
    class MessageBoxMock:
        def __init__(self):
            self.calls = []
        def showerror(self, title, message):
            self.calls.append({"type": "error", "title": title, "message": message})
        def showinfo(self, title, message):
            self.calls.append({"type": "info", "title": title, "message": message})
        def get_last_call(self):
            return self.calls[-1] if self.calls else None
        def clear(self):
            self.calls.clear()

    mock = MessageBoxMock()
    monkeypatch.setattr("app.ui.patient_window.messagebox.showerror", mock.showerror)
    monkeypatch.setattr("app.ui.patient_window.messagebox.showinfo", mock.showinfo)
    return mock


@pytest.fixture
def service():
    return PatientService(DummyRepo())


def fill(entry, text):
    entry.delete(0, "end")
    entry.insert(0, text)


def click_save(window):
    for widget in window.winfo_children():
        btn = _find_button(widget, "Salvar Cadastro")
        if btn:
            btn.invoke()
            return


def _find_button(widget, text):
    import tkinter.ttk as ttk
    try:
        if isinstance(widget, ttk.Button) and widget.cget("text") == text:
            return widget
    except:
        pass
    for child in widget.winfo_children():
        result = _find_button(child, text)
        if result:
            return result
    return None


def test_sem_nome_erro(root, mock_messagebox, service):
    captured = []
    
    def on_save(patient):
        result = service.validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))
        captured.append(patient)
        return True

    window = PatientFormWindow(parent=root, patient=None, on_save=on_save)
    click_save(window)

    call = mock_messagebox.get_last_call()
    assert call is not None
    assert call["type"] == "error"
    assert "nome" in call["message"].lower()
    assert len(captured) == 0
    window.destroy()


def test_sem_telefone_erro(root, mock_messagebox, service):
    captured = []
    mock_messagebox.clear()
    
    def on_save(patient):
        result = service.validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))
        captured.append(patient)
        return True

    window = PatientFormWindow(parent=root, patient=None, on_save=on_save)
    fill(window.name_entry, "Maria Silva")
    click_save(window)

    call = mock_messagebox.get_last_call()
    assert call is not None
    assert call["type"] == "error"
    assert "telefone" in call["message"].lower()
    assert len(captured) == 0
    window.destroy()


def test_sem_data_erro(root, mock_messagebox, service):
    captured = []
    mock_messagebox.clear()
    
    def on_save(patient):
        result = service.validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))
        captured.append(patient)
        return True

    window = PatientFormWindow(parent=root, patient=None, on_save=on_save)
    fill(window.name_entry, "Maria Silva")
    fill(window.phone_entry, format_phone("21999998888"))
    
    if hasattr(window, 'birth_date_entry'):
        window.birth_date_entry.delete(0, "end")
    
    click_save(window)

    call = mock_messagebox.get_last_call()
    assert call is not None
    assert call["type"] == "error"
    assert "data" in call["message"].lower()
    assert len(captured) == 0
    window.destroy()


def test_email_invalido_erro(root, mock_messagebox, service):
    captured = []
    mock_messagebox.clear()
    
    def on_save(patient):
        result = service.validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))
        captured.append(patient)
        return True

    window = PatientFormWindow(parent=root, patient=None, on_save=on_save)
    fill(window.name_entry, "Maria Silva")
    fill(window.phone_entry, format_phone("21999998888"))
    fill(window.email_entry, "email-invalido")
    
    if hasattr(window, 'birth_date_entry'):
        fill(window.birth_date_entry, "15/06/1990")
    else:
        window.birth_date_picker.set_date(date(1990, 6, 15))
    
    click_save(window)

    call = mock_messagebox.get_last_call()
    assert call is not None
    assert call["type"] == "error"
    assert "e-mail" in call["message"].lower() or "email" in call["message"].lower()
    assert len(captured) == 0
    window.destroy()


def test_dados_validos_sucesso(root, mock_messagebox, service):
    captured = []
    mock_messagebox.clear()
    
    def on_save(patient):
        result = service.validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))
        captured.append(patient)
        return True

    window = PatientFormWindow(parent=root, patient=None, on_save=on_save)
    fill(window.name_entry, "Maria Silva")
    fill(window.phone_entry, format_phone("21999998888"))
    fill(window.email_entry, "maria@email.com")
    
    if hasattr(window, 'birth_date_entry'):
        fill(window.birth_date_entry, "15/06/1990")
    else:
        window.birth_date_picker.set_date(date(1990, 6, 15))
    
    click_save(window)

    errors = [c for c in mock_messagebox.calls if c["type"] == "error"]
    assert len(errors) == 0
    assert len(captured) == 1
    assert captured[0].name == "Maria Silva"
    assert captured[0].email == "maria@email.com"
    window.destroy()
