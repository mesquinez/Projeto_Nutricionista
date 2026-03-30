from datetime import date

import pytest
import tkinter as tk

from app.models.patient import Patient
from app.ui.anamnese_window import AnamneseWindow


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    try:
        root.destroy()
    except Exception:
        pass


@pytest.fixture
def sample_patients():
    return [
        Patient(
            id=1,
            name="Maria Silva",
            phone="(21) 99999-8888",
            birth_date=date(1990, 5, 10),
            status="Ativo",
        ),
        Patient(
            id=2,
            name="Joao Costa",
            phone="(21) 98888-7777",
            birth_date=date(1985, 8, 22),
            status="Inativo",
        ),
    ]


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
            if not self.calls:
                return None
            return self.calls[-1]

    mock_instance = MessageBoxMock()
    monkeypatch.setattr("app.ui.anamnese_window.messagebox.showerror", mock_instance.showerror)
    monkeypatch.setattr("app.ui.anamnese_window.messagebox.showinfo", mock_instance.showinfo)
    return mock_instance


def _set_text(widget, content: str):
    widget.delete("1.0", "end")
    widget.insert("1.0", content)


def test_preseleciona_paciente_e_carrega_resumo(root, sample_patients):
    window = AnamneseWindow(root, patient=sample_patients[0], patients=sample_patients)

    assert window.selected_patient == sample_patients[0]
    assert window.patient_var.get() == "1 - Maria Silva"
    assert window.patient_name_value.cget("text") == "Maria Silva"
    assert window.patient_birth_value.cget("text") == "10/05/1990"
    assert window.patient_phone_value.cget("text") == "(21) 99999-8888"
    assert window.patient_status_value.cget("text") == "Ativo"

    window.destroy()


def test_salvar_monta_anamnese_com_patient_id_do_paciente_selecionado(root, sample_patients):
    captured = []

    def on_save(anamnese):
        captured.append(anamnese)
        return True

    window = AnamneseWindow(root, patients=sample_patients, on_save=on_save)

    window.patient_var.set("2 - Joao Costa")
    window._on_patient_selected()

    if hasattr(window, "data_entry"):
        window.data_entry.insert(0, "27/03/2026")
    else:
        window.data_picker.set_date(date(2026, 3, 27))

    _set_text(window.text_fields["queixa_principal"], "Dificuldade para emagrecer")
    _set_text(window.text_fields["objetivo"], "Melhorar alimentacao")

    window._save()

    assert len(captured) == 1
    saved = captured[0]
    assert saved.patient_id == 2
    assert saved.data == date(2026, 3, 27)
    assert saved.queixa_principal == "Dificuldade para emagrecer"
    assert saved.objetivo == "Melhorar alimentacao"


def test_salvar_sem_paciente_exibe_erro(root, sample_patients, mock_messagebox):
    captured = []

    def on_save(anamnese):
        captured.append(anamnese)
        return True

    window = AnamneseWindow(root, patients=sample_patients, on_save=on_save)
    window.patient_var.set("")
    window.selected_patient = None

    if hasattr(window, "data_entry"):
        window.data_entry.insert(0, "27/03/2026")
    else:
        window.data_picker.set_date(date(2026, 3, 27))

    _set_text(window.text_fields["queixa_principal"], "Dificuldade para emagrecer")

    window._save()

    call = mock_messagebox.get_last_call()
    assert call is not None
    assert call["type"] == "error"
    assert "selecione um paciente" in call["message"].lower()
    assert captured == []

    window.destroy()


def test_salvar_sem_data_exibe_erro(root, sample_patients, mock_messagebox, monkeypatch):
    captured = []

    def on_save(anamnese):
        captured.append(anamnese)
        return True

    window = AnamneseWindow(root, patient=sample_patients[0], patients=sample_patients, on_save=on_save)
    _set_text(window.text_fields["queixa_principal"], "Dificuldade para emagrecer")

    if hasattr(window, "data_entry"):
        window.data_entry.delete(0, "end")
    else:
        monkeypatch.setattr(window.data_picker, "get_date", lambda: None)

    window._save()

    call = mock_messagebox.get_last_call()
    assert call is not None
    assert call["type"] == "error"
    assert "data" in call["message"].lower()
    assert captured == []

    window.destroy()


def test_salvar_sem_queixa_principal_envia_para_validacao_do_fluxo(root, sample_patients):
    captured = []

    def on_save(anamnese):
        captured.append(anamnese)
        return False

    window = AnamneseWindow(root, patient=sample_patients[0], patients=sample_patients, on_save=on_save)

    if hasattr(window, "data_entry"):
        window.data_entry.insert(0, "27/03/2026")
    else:
        window.data_picker.set_date(date(2026, 3, 27))

    window._save()

    assert len(captured) == 1
    assert captured[0].patient_id == 1
    assert captured[0].queixa_principal == ""
    assert window.winfo_exists() == 1

    window.destroy()
