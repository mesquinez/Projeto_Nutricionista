import os
import tempfile
from datetime import date

import pytest

from app.controllers.anamnese_controller import AnamneseController
from app.controllers.avaliacao_controller import AvaliacaoController
from app.controllers.consulta_controller import ConsultaController
from app.controllers.patient_controller import PatientController
from app.controllers.plano_alimentar_controller import PlanoAlimentarController
from app.models.patient import Patient
from app.repositories.sqlite_anamnese_repository import SQLiteAnamneseRepository
from app.repositories.sqlite_avaliacao_repository import SQLiteAvaliacaoRepository
from app.repositories.sqlite_consulta_repository import SQLiteConsultaRepository
from app.repositories.sqlite_patient_repository import SQLitePatientRepository
from app.repositories.sqlite_plano_alimentar_repository import SQLitePlanoAlimentarRepository
from app.services.anamnese_service import AnamneseService
from app.services.avaliacao_service import AvaliacaoService
from app.services.consulta_service import ConsultaService
from app.services.patient_service import PatientService
from app.services.plano_alimentar_service import PlanoAlimentarService
from app.ui.main_window import MainWindow
from app.ui.patient_detail_window import PatientDetailWindow


def _build_main_window(db_path: str) -> MainWindow:
    patient_repo = SQLitePatientRepository(db_path)
    anamnese_repo = SQLiteAnamneseRepository(db_path)
    consulta_repo = SQLiteConsultaRepository(db_path)
    avaliacao_repo = SQLiteAvaliacaoRepository(db_path)
    plano_repo = SQLitePlanoAlimentarRepository(db_path)

    patient_repo._init_db()
    anamnese_repo._init_db()
    consulta_repo._init_db()
    avaliacao_repo._init_db()
    plano_repo._init_db()

    return MainWindow(
        patient_controller=PatientController(PatientService(patient_repo)),
        anamnese_controller=AnamneseController(AnamneseService(anamnese_repo)),
        consulta_controller=ConsultaController(ConsultaService(consulta_repo)),
        avaliacao_controller=AvaliacaoController(AvaliacaoService(avaliacao_repo)),
        plano_controller=PlanoAlimentarController(PlanoAlimentarService(plano_repo)),
    )


def _find_anamnese_window(root):
    for child in root.winfo_children():
        try:
            if child.winfo_exists() and child.title() == "Anamnese":
                return child
        except Exception:
            continue
    return None


@pytest.fixture
def temp_db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def mock_messagebox(monkeypatch):
    class MessageBoxMock:
        def __init__(self):
            self.calls = []
            self.askyesno_response = True

        def showerror(self, title, message):
            self.calls.append({"type": "error", "title": title, "message": message})

        def showinfo(self, title, message):
            self.calls.append({"type": "info", "title": title, "message": message})

        def askyesno(self, title, message):
            self.calls.append({"type": "askyesno", "title": title, "message": message})
            return self.askyesno_response

    mock = MessageBoxMock()
    monkeypatch.setattr("app.ui.main_window.messagebox.showerror", mock.showerror)
    monkeypatch.setattr("app.ui.main_window.messagebox.showinfo", mock.showinfo)
    monkeypatch.setattr("app.ui.main_window.messagebox.askyesno", mock.askyesno)
    monkeypatch.setattr("app.ui.anamnese_window.messagebox.showerror", mock.showerror)
    monkeypatch.setattr("app.ui.anamnese_window.messagebox.showinfo", mock.showinfo)
    monkeypatch.setattr("app.ui.patient_detail_window.messagebox.showerror", mock.showerror)
    monkeypatch.setattr("app.ui.patient_detail_window.messagebox.showinfo", mock.showinfo)
    return mock


@pytest.fixture
def main_window(temp_db_path, mock_messagebox):
    window = _build_main_window(temp_db_path)
    yield window
    try:
        for child in window.root.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        window.root.destroy()
    except Exception:
        pass


def _set_text(widget, content: str):
    widget.delete("1.0", "end")
    widget.insert("1.0", content)


def test_add_patient_oferece_abertura_da_anamnese_com_paciente_criado(main_window, monkeypatch):
    created_patient = Patient(
        name="Maria Silva",
        phone="(21) 99999-8888",
        birth_date=date(1990, 5, 10),
        email="maria@email.com",
    )
    opened = {}

    class FakePatientFormWindow:
        def __init__(self, parent, patient=None, on_save=None):
            assert patient is None
            assert on_save is not None
            on_save(created_patient)

    monkeypatch.setattr("app.ui.patient_window.PatientFormWindow", FakePatientFormWindow)
    monkeypatch.setattr(main_window.root, "after", lambda delay, callback: callback())
    monkeypatch.setattr(
        main_window,
        "_open_anamnese_for_patient",
        lambda patient: opened.setdefault("patient", patient),
    )

    main_window._add_patient()

    assert opened["patient"].id is not None
    assert opened["patient"].name == "Maria Silva"
    row_values = main_window.tree.item(opened["patient"].id, "values")
    assert row_values[1] == "Maria Silva"


def test_salvar_anamnese_atualiza_lista_principal_e_prontuario(main_window):
    patient = main_window.patient_controller.create_patient(
        Patient(
            name="Maria Silva",
            phone="(21) 99999-8888",
            birth_date=date(1990, 5, 10),
            email="maria@email.com",
        )
    )
    main_window._load_patients()

    main_window._open_anamnese_for_patient(patient)
    anamnese_window = _find_anamnese_window(main_window.root)

    assert anamnese_window is not None
    assert anamnese_window.patient_var.get() == f"{patient.id} - {patient.name}"

    if hasattr(anamnese_window, "data_entry"):
        anamnese_window.data_entry.insert(0, "27/03/2026")
    else:
        anamnese_window.data_picker.set_date(date(2026, 3, 27))

    _set_text(anamnese_window.text_fields["queixa_principal"], "Dificuldade para emagrecer")
    _set_text(anamnese_window.text_fields["objetivo"], "Melhorar alimentacao")
    anamnese_window._save()

    main_window._load_patients()
    row_values = main_window.tree.item(patient.id, "values")
    assert row_values[5] == "✅"

    detail_window = PatientDetailWindow(
        main_window.root,
        patient=patient,
        patient_controller=main_window.patient_controller,
        anamnese_controller=main_window.anamnese_controller,
        consulta_controller=main_window.consulta_controller,
        avaliacao_controller=main_window.avaliacao_controller,
        plano_controller=main_window.plano_controller,
    )

    anamneses = detail_window.anamneses_tree.get_children()
    assert len(anamneses) == 1
    assert detail_window.anamneses_tree.item(anamneses[0], "values")[1] == "Dificuldade para emagrecer"
    resumo = detail_window.resumo_text.get("1.0", "end")
    assert "ANAMNESE (27/03/2026)" in resumo
    assert "Queixa principal: Dificuldade para emagrecer" in resumo

    detail_window.destroy()
