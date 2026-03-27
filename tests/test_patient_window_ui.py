import pytest
import tkinter as tk
from unittest.mock import MagicMock

from app.ui.patient_window import PatientFormWindow
from app.services.patient_service import PatientService
from app.repositories.patient_repository import PatientRepository


# -----------------------------------------------------------------------
# DummyRepo — repositório que não persiste nada (para testes de validação)
# -----------------------------------------------------------------------
class DummyRepo(PatientRepository):
    def add(self, patient): return 1
    def update(self, patient): return True
    def delete(self, patient_id): return True
    def get_by_id(self, patient_id): return None
    def get_all(self): return []
    def search(self, query): return []

@pytest.fixture
def root():
    """Cria a janela principal (root) do Tkinter invisível para os testes."""
    root = tk.Tk()
    root.withdraw()
    yield root
    try:
        root.destroy()
    except:
        pass

@pytest.fixture
def mock_messagebox(monkeypatch):
    """
    Mock para interceptar messagebox.showerror e messagebox.showinfo.
    Armazena em memória para recuperar a última chamada.
    """
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

        def clear(self):
            self.calls.clear()

    mock_instance = MessageBoxMock()
    monkeypatch.setattr("app.ui.patient_window.messagebox.showerror", mock_instance.showerror)
    monkeypatch.setattr("app.ui.patient_window.messagebox.showinfo", mock_instance.showinfo)
    
    return mock_instance

@pytest.fixture(scope="module")
def service():
    """PatientService real com repositório dummy — executa validação de verdade."""
    return PatientService(DummyRepo())


@pytest.fixture
def captured_save_calls():
    """Armazena os pacientes que o on_save recebeu, para inspeção posterior."""
    return []


@pytest.fixture
def patient_window(root, service, captured_save_calls):
    """
    Janela de cadastro com on_save que usa validação real.
    Levanta ValueError em caso de falha — o except da janela chama messagebox.showerror.
    """
    def on_save(patient):
        result = service.validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))
        captured_save_calls.append(patient)
        return True

    window = PatientFormWindow(parent=root, patient=None, on_save=on_save)
    yield window
    window.destroy()


# ---------------------------------------------------------------------------
# Helpers de interação com UI
# ---------------------------------------------------------------------------

def fill_entry(entry, text: str, root=None):
    entry.delete(0, "end")
    entry.insert(0, text)
    return entry


def type_into_entry(entry, text: str, root=None):
    for char in text:
        current = entry.get()
        entry.delete(0, "end")
        entry.insert(0, current + char)
    return entry


def click_button(button, root=None):
    button.invoke()


def fill_text_widget(text_widget, content: str, root=None):
    text_widget.delete("1.0", "end")
    text_widget.insert("1.0", content)


def get_button_by_text(window, label: str):
    """
    Percorre os widgets da janela e retorna o primeiro botão com o texto indicado.
    Útil para encontrar botões como 'Salvar Cadastro' ou 'Cancelar'.
    """
    for widget in window.winfo_children():
        result = _find_button_recursive(widget, label)
        if result:
            return result
    return None


def _find_button_recursive(widget, label: str):
    """Busca recursiva em sub-widgets."""
    import tkinter.ttk as ttk
    try:
        if isinstance(widget, ttk.Button) and widget.cget("text") == label:
            return widget
    except Exception:
        pass
    for child in widget.winfo_children():
        result = _find_button_recursive(child, label)
        if result:
            return result
    return None


# ---------------------------------------------------------------------------
# Testes de infraestrutura
# ---------------------------------------------------------------------------

def test_estrutura_basica(patient_window):
    """Valida criação e estado inicial da janela."""
    assert patient_window is not None
    assert patient_window.title() == "Cadastro de Paciente"


def test_helpers_funcionam(patient_window, root):
    """Valida que os helpers de interação não lançam exceção."""
    fill_entry(patient_window.name_entry, "Maria Silva", root)
    assert patient_window.name_entry.get() == "Maria Silva"

    btn_cancelar = get_button_by_text(patient_window, "Cancelar")
    assert btn_cancelar is not None


# -----------------------------------------------------------------------
# Testes de UI — cenários reais de interação
# -----------------------------------------------------------------------

def test_salvar_sem_nome_exibe_erro(patient_window, mock_messagebox, captured_save_calls, root):
    """
    Cenário: usuário clica em Salvar sem preencher o nome.
    Esperado:
      - messagebox.showerror é chamado
      - mensagem menciona 'nome'
      - o serviço NÃO recebe o paciente (lista captured_save_calls permanece vazia)
    """
    # Não preenche nada — nome propositalmente vazio

    btn_salvar = get_button_by_text(patient_window, "Salvar Cadastro")
    assert btn_salvar is not None, "Botão 'Salvar Cadastro' não encontrado"

    click_button(btn_salvar, root)

    # Verifica que houve um erro exibido
    call = mock_messagebox.get_last_call()
    assert call is not None, "Nenhum messagebox foi chamado"
    assert call["type"] == "error"
    assert "nome" in call["message"].lower(), (
        f"Esperava mensagem sobre 'nome', mas recebi: {call['message']}"
    )

    # Verifica que o serviço nunca persistiu nada
    assert len(captured_save_calls) == 0, "Serviço foi chamado mesmo com nome vazio"


def test_salvar_sem_telefone_exibe_erro(patient_window, mock_messagebox, captured_save_calls, root):
    """
    Cenário: usuário preenche nome mas deixa telefone em branco.
    Esperado:
      - messagebox.showerror é chamado
      - mensagem menciona 'telefone'
      - o serviço NÃO recebe o paciente
    """
    fill_entry(patient_window.name_entry, "Maria Silva", root)
    # Telefone propositalmente vazio

    btn_salvar = get_button_by_text(patient_window, "Salvar Cadastro")
    assert btn_salvar is not None, "Botão 'Salvar Cadastro' não encontrado"

    click_button(btn_salvar, root)

    call = mock_messagebox.get_last_call()
    assert call is not None, "Nenhum messagebox foi chamado"
    assert call["type"] == "error"
    assert "telefone" in call["message"].lower(), (
        f"Esperava mensagem sobre 'telefone', mas recebi: {call['message']}"
    )

    assert len(captured_save_calls) == 0, "Serviço foi chamado mesmo sem telefone"


def test_salvar_sem_data_nascimento_exibe_erro(patient_window, mock_messagebox, captured_save_calls, root):
    """
    Cenário: usuário preenche nome e telefone mas não informa data de nascimento.
    Esperado:
      - showerror chamado
      - mensagem menciona 'data'
      - serviço NÃO é chamado
    """
    from app.ui.patient_window import HAS_TKCALENDAR

    fill_entry(patient_window.name_entry, "Ana Lima", root)
    fill_entry(patient_window.phone_entry, "21999998888", root)

    # Se tkcalendar está presente, ele já inicia com a data atual — precisamos
    # abortar esse teste pois não há como esvaziar o DateEntry limpo.
    # Somente testamos o path do Entry manual.
    if HAS_TKCALENDAR:
        pytest.skip("DateEntry sempre tem uma data; teste válido apenas sem tkcalendar")

    patient_window.birth_date_entry.delete(0, "end")
    root.update_idletasks()

    btn_salvar = get_button_by_text(patient_window, "Salvar Cadastro")
    click_button(btn_salvar, root)

    call = mock_messagebox.get_last_call()
    assert call is not None, "Nenhum messagebox foi chamado"
    assert call["type"] == "error"
    assert "data" in call["message"].lower(), (
        f"Esperava mensagem sobre 'data', mas recebi: {call['message']}"
    )
    assert len(captured_save_calls) == 0, "Serviço foi chamado mesmo sem data de nascimento"


def test_email_invalido_exibe_erro(patient_window, mock_messagebox, captured_save_calls, root):
    """
    Cenário: usuário preenche campos obrigatórios mas informa e-mail malformado.
    Esperado:
      - showerror chamado
      - mensagem menciona 'e-mail'
      - serviço NÃO é chamado
    """
    from datetime import date
    from app.ui.patient_window import HAS_TKCALENDAR

    fill_entry(patient_window.name_entry, "Carlos Melo", root)
    fill_entry(patient_window.phone_entry, "21999998888", root)
    fill_entry(patient_window.email_entry, "email-invalido-sem-arroba", root)

    if HAS_TKCALENDAR:
        patient_window.birth_date_picker.set_date(date(1990, 6, 15))
    else:
        fill_entry(patient_window.birth_date_entry, "15/06/1990", root)

    btn_salvar = get_button_by_text(patient_window, "Salvar Cadastro")
    click_button(btn_salvar, root)

    call = mock_messagebox.get_last_call()
    assert call is not None, "Nenhum messagebox foi chamado"
    assert call["type"] == "error"
    assert "e-mail" in call["message"].lower() or "email" in call["message"].lower(), (
        f"Esperava mensagem sobre 'e-mail', mas recebi: {call['message']}"
    )
    assert len(captured_save_calls) == 0, "Serviço foi chamado com e-mail inválido"


def test_telefone_formato_invalido_exibe_erro(patient_window, mock_messagebox, captured_save_calls, root):
    """
    Cenário: usuário digita telefone sem máscara (só números sem formatação).
    Esperado:
      - showerror chamado
      - mensagem menciona 'telefone'
      - serviço NÃO é chamado
    """
    from datetime import date
    from app.ui.patient_window import HAS_TKCALENDAR

    fill_entry(patient_window.name_entry, "Pedro Costa", root)
    # Insere direto no campo - SEM event_generate para evitar travamento na máscara
    patient_window.phone_entry.insert(0, "9999")

    if HAS_TKCALENDAR:
        patient_window.birth_date_picker.set_date(date(1985, 3, 20))
    else:
        fill_entry(patient_window.birth_date_entry, "20/03/1985", root)

    btn_salvar = get_button_by_text(patient_window, "Salvar Cadastro")
    click_button(btn_salvar, root)

    call = mock_messagebox.get_last_call()
    assert call is not None, "Nenhum messagebox foi chamado"
    assert call["type"] == "error"
    assert "telefone" in call["message"].lower(), (
        f"Esperava mensagem sobre 'telefone', mas recebi: {call['message']}"
    )
    assert len(captured_save_calls) == 0, "Serviço foi chamado com telefone inválido"


def test_cadastro_valido_completo(patient_window, mock_messagebox, captured_save_calls, root):
    """
    Cenário: usuário preenche todos os campos obrigatórios corretamente.
    Esperado:
      - nenhum showerror é chamado
      - o serviço recebe exatamente 1 paciente
      - dados do paciente correspondem ao que foi digitado
    """
    from datetime import date
    from app.ui.patient_window import HAS_TKCALENDAR

    from app.ui.utils.formatters import format_phone

    fill_entry(patient_window.name_entry, "Juliana Ferreira", root)
    fill_entry(patient_window.social_name_entry, "Ju", root)
    # Insere o telefone já formatado, como estaria após a máscara ser aplicada
    fill_entry(patient_window.phone_entry, format_phone("21999998888"), root)
    fill_entry(patient_window.email_entry, "ju@email.com", root)
    fill_entry(patient_window.city_entry, "Rio de Janeiro", root)
    fill_entry(patient_window.uf_entry, "RJ", root)
    fill_entry(patient_window.profession_entry, "Médica", root)

    if HAS_TKCALENDAR:
        patient_window.birth_date_picker.set_date(date(1992, 8, 10))
    else:
        fill_entry(patient_window.birth_date_entry, "10/08/1992", root)

    btn_salvar = get_button_by_text(patient_window, "Salvar Cadastro")
    click_button(btn_salvar, root)

    # Nenhum erro deve ter sido chamado
    error_calls = [c for c in mock_messagebox.calls if c["type"] == "error"]
    assert len(error_calls) == 0, f"Erros inesperados: {error_calls}"

    # Exatamente 1 paciente salvo
    assert len(captured_save_calls) == 1, "Esperava 1 paciente salvo"

    saved = captured_save_calls[0]
    assert saved.name == "Juliana Ferreira"
    assert saved.social_name == "Ju"
    assert saved.city == "Rio de Janeiro"
    assert saved.uf == "RJ"
    assert saved.profession == "Médica"


def test_salvar_sem_data_nascimento_exibe_erro_universal(patient_window, mock_messagebox, captured_save_calls, root, monkeypatch):
    """
    Cenário: usuário preenche nome e telefone mas não informa data de nascimento.
    Funciona com ou sem tkcalendar instalado.
    Esperado:
      - showerror chamado
      - mensagem menciona 'data'
      - serviço NÃO é chamado
    """
    from app.ui.utils.formatters import format_phone
    from app.ui.patient_window import HAS_TKCALENDAR

    fill_entry(patient_window.name_entry, "Roberto Alves", root)
    fill_entry(patient_window.phone_entry, format_phone("21988887777"), root)

    if HAS_TKCALENDAR:
        # DateEntry sempre tem uma data — forçamos get_date a retornar None
        # para simular ausência de data no path de validação
        monkeypatch.setattr(patient_window.birth_date_picker, "get_date", lambda: None)
    else:
        # Entry manual: simplesmente esvazia o campo
        patient_window.birth_date_entry.delete(0, "end")
        root.update_idletasks()

    btn_salvar = get_button_by_text(patient_window, "Salvar Cadastro")
    assert btn_salvar is not None, "Botão 'Salvar Cadastro' não encontrado"

    click_button(btn_salvar, root)

    call = mock_messagebox.get_last_call()
    assert call is not None, "Nenhum messagebox foi chamado"
    assert call["type"] == "error"
    assert "data" in call["message"].lower(), (
        f"Esperava mensagem sobre 'data', mas recebi: {call['message']}"
    )
    assert len(captured_save_calls) == 0, "Serviço foi chamado mesmo sem data de nascimento"


def test_cadastro_completo_com_showinfo(root, mock_messagebox, monkeypatch):
    """
    Cenário: usuário preenche todos os campos corretamente e salva.
    Simula o on_save da main_window: valida, persiste, exibe showinfo.
    Esperado:
      - serviço recebe exatamente 1 paciente
      - messagebox.showinfo é chamado
      - dados enviados estão corretos
      - nenhum showerror ocorre
    """
    from datetime import date
    from app.ui.utils.formatters import format_phone
    from app.ui.patient_window import PatientFormWindow, HAS_TKCALENDAR

    save_calls = []

    def on_save_with_feedback(patient):
        """Replica o comportamento de main_window._add_patient.on_save."""
        result = PatientService(DummyRepo()).validate(patient)
        if not result.success:
            raise ValueError("; ".join(result.error_messages))
        save_calls.append(patient)
        # Simula o showinfo que main_window exibe após salvar
        from tkinter import messagebox as mb
        mb.showinfo("Sucesso", f"Paciente {patient.name} cadastrado!")
        return True

    window = PatientFormWindow(parent=root, patient=None, on_save=on_save_with_feedback)

    fill_entry(window.name_entry, "Fernanda Souza", root)
    fill_entry(window.social_name_entry, "Fer", root)
    fill_entry(window.phone_entry, format_phone("21977776666"), root)
    fill_entry(window.email_entry, "fernanda@email.com", root)
    fill_entry(window.city_entry, "Niterói", root)
    fill_entry(window.uf_entry, "RJ", root)
    fill_entry(window.profession_entry, "Advogada", root)
    fill_text_widget(window.obs_text, "Alergia a frutos do mar.", root)

    if HAS_TKCALENDAR:
        window.birth_date_picker.set_date(date(1988, 11, 25))
    else:
        fill_entry(window.birth_date_entry, "25/11/1988", root)

    btn_salvar = get_button_by_text(window, "Salvar Cadastro")
    assert btn_salvar is not None, "Botão 'Salvar Cadastro' não encontrado"
    click_button(btn_salvar, root)

    # Nenhum erro
    error_calls = [c for c in mock_messagebox.calls if c["type"] == "error"]
    assert len(error_calls) == 0, f"Erros inesperados: {error_calls}"

    # showinfo foi chamado com conteúdo correto
    info_calls = [c for c in mock_messagebox.calls if c["type"] == "info"]
    assert len(info_calls) == 1, "showinfo não foi chamado"
    assert "Fernanda Souza" in info_calls[0]["message"], (
        f"Nome não aparece no showinfo: {info_calls[0]['message']}"
    )

    # Serviço recebeu exatamente 1 paciente com dados corretos
    assert len(save_calls) == 1, "Esperava 1 paciente salvo"
    saved = save_calls[0]
    assert saved.name == "Fernanda Souza"
    assert saved.social_name == "Fer"
    assert saved.email == "fernanda@email.com"
    assert saved.city == "Niterói"
    assert saved.uf == "RJ"
    assert saved.profession == "Advogada"
    assert saved.observations == "Alergia a frutos do mar."
    assert saved.birth_date == date(1988, 11, 25)

