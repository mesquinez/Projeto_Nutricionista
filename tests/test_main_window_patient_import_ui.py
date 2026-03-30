import os
import tempfile
from pathlib import Path

import pytest

from app.controllers.anamnese_controller import AnamneseController
from app.controllers.avaliacao_controller import AvaliacaoController
from app.controllers.consulta_controller import ConsultaController
from app.controllers.patient_controller import PatientController
from app.controllers.plano_alimentar_controller import PlanoAlimentarController
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


@pytest.fixture
def temp_db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def mock_dialogs(monkeypatch):
    class DialogMock:
        def __init__(self):
            self.open_path = ""
            self.calls = []

        def askopenfilename(self, **kwargs):
            self.calls.append({"type": "open", "kwargs": kwargs})
            return self.open_path

        def showinfo(self, title, message):
            self.calls.append({"type": "info", "title": title, "message": message})

        def showerror(self, title, message):
            self.calls.append({"type": "error", "title": title, "message": message})

    mock = DialogMock()
    monkeypatch.setattr("app.ui.main_window.filedialog.askopenfilename", mock.askopenfilename)
    monkeypatch.setattr("app.ui.main_window.messagebox.showinfo", mock.showinfo)
    monkeypatch.setattr("app.ui.main_window.messagebox.showerror", mock.showerror)
    return mock


@pytest.fixture
def main_window(temp_db_path):
    window = _build_main_window(temp_db_path)
    yield window
    try:
        window.root.destroy()
    except Exception:
        pass


def test_importacao_pela_tela_exibe_resumo_e_atualiza_lista(main_window, mock_dialogs):
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    csv_path = Path(path)
    csv_path.write_text(
        "\n".join(
            [
                "nome_completo,data_nascimento,telefone",
                "Maria Silva,10/05/1990,(21)99999-8888",
                "Linha Sem Telefone,10/05/1990,",
            ]
        ),
        encoding="utf-8",
    )
    mock_dialogs.open_path = str(csv_path)

    try:
        main_window._import_patients()

        assert len(main_window.tree.get_children()) == 1
        info_calls = [call for call in mock_dialogs.calls if call["type"] == "info"]
        assert len(info_calls) == 1
        message = info_calls[0]["message"]
        assert "Pacientes importados com sucesso: 1" in message
        assert "Linhas com falha: 1" in message
        assert "Linha 3:" in message
    finally:
        csv_path.unlink(missing_ok=True)
