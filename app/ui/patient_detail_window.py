import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.patient import Patient
    from ..controllers.patient_controller import PatientController
    from ..controllers.anamnese_controller import AnamneseController
    from ..controllers.consulta_controller import ConsultaController
    from ..controllers.avaliacao_controller import AvaliacaoController
    from ..controllers.plano_alimentar_controller import PlanoAlimentarController


class PatientDetailWindow(tk.Toplevel):
    def __init__(
        self,
        parent,
        patient: "Patient",
        patient_controller: "PatientController",
        anamnese_controller: "AnamneseController",
        consulta_controller: "ConsultaController",
        avaliacao_controller: "AvaliacaoController",
        plano_controller: "PlanoAlimentarController",
    ):
        super().__init__(parent)
        self.patient = patient
        self.patient_controller = patient_controller
        self.anamnese_controller = anamnese_controller
        self.consulta_controller = consulta_controller
        self.avaliacao_controller = avaliacao_controller
        self.plano_controller = plano_controller

        self.title(f"Paciente: {patient.name}")
        self.geometry("900x700")
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_consultas = ttk.Frame(notebook)
        self.tab_avaliacoes = ttk.Frame(notebook)
        self.tab_planos = ttk.Frame(notebook)
        self.tab_resumo = ttk.Frame(notebook)

        notebook.add(self.tab_consultas, text="📅 Consultas")
        notebook.add(self.tab_avaliacoes, text="📏 Avaliações")
        notebook.add(self.tab_planos, text="🍽️ Planos")
        notebook.add(self.tab_resumo, text="📊 Resumo")

        self._create_consultas_tab()
        self._create_avaliacoes_tab()
        self._create_planos_tab()
        self._create_resumo_tab()

        ttk.Frame(self).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(self, text="Fechar", command=self.destroy).pack(pady=10)

    def _create_consultas_tab(self):
        frame = ttk.Frame(self.tab_consultas, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Button(frame, text="+ Nova Consulta", command=self._nova_consulta).pack(anchor="w", pady=5)

        cols = ("date", "queixa", "conduta", "peso")
        self.consultas_tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)

        self.consultas_tree.heading("date", text="Data")
        self.consultas_tree.heading("queixa", text="Queixa")
        self.consultas_tree.heading("conduta", text="Conduta")
        self.consultas_tree.heading("peso", text="Peso (kg)")

        self.consultas_tree.column("date", width=100)
        self.consultas_tree.column("queixa", width=250)
        self.consultas_tree.column("conduta", width=300)
        self.consultas_tree.column("peso", width=80)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.consultas_tree.yview)
        self.consultas_tree.configure(yscrollcommand=scrollbar.set)

        self.consultas_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        self.consultas_tree.bind("<Double-1>", lambda e: self._editar_consulta())

    def _create_avaliacoes_tab(self):
        frame = ttk.Frame(self.tab_avaliacoes, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Button(frame, text="+ Nova Avaliação", command=self._nova_avaliacao).pack(anchor="w", pady=5)

        cols = ("date", "peso", "altura", "imc", "cintura", "quadril")
        self.avaliacoes_tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)

        self.avaliacoes_tree.heading("date", text="Data")
        self.avaliacoes_tree.heading("peso", text="Peso")
        self.avaliacoes_tree.heading("altura", text="Altura")
        self.avaliacoes_tree.heading("imc", text="IMC")
        self.avaliacoes_tree.heading("cintura", text="Cintura")
        self.avaliacoes_tree.heading("quadril", text="Quadril")

        for col in cols:
            self.avaliacoes_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.avaliacoes_tree.yview)
        self.avaliacoes_tree.configure(yscrollcommand=scrollbar.set)

        self.avaliacoes_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        self.avaliacoes_tree.bind("<Double-1>", lambda e: self._editar_avaliacao())

    def _create_planos_tab(self):
        frame = ttk.Frame(self.tab_planos, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Button(frame, text="+ Novo Plano", command=self._novo_plano).pack(anchor="w", pady=5)

        cols = ("date", "calorias", "proteinas", "carboidratos", "gorduras")
        self.planos_tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)

        self.planos_tree.heading("date", text="Data")
        self.planos_tree.heading("calorias", text="Calorias")
        self.planos_tree.heading("proteinas", text="Proteínas")
        self.planos_tree.heading("carboidratos", text="Carboidratos")
        self.planos_tree.heading("gorduras", text="Gorduras")

        for col in cols:
            self.planos_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.planos_tree.yview)
        self.planos_tree.configure(yscrollcommand=scrollbar.set)

        self.planos_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        self.planos_tree.bind("<Double-1>", lambda e: self._editar_plano())

    def _create_resumo_tab(self):
        frame = ttk.Frame(self.tab_resumo, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        self.resumo_text = tk.Text(frame, wrap="word", font=("TkDefaultFont", 10))
        self.resumo_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.resumo_text.yview)
        self.resumo_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def _load_data(self):
        self._load_consultas()
        self._load_avaliacoes()
        self._load_planos()
        self._load_resumo()

    def _load_consultas(self):
        for item in self.consultas_tree.get_children():
            self.consultas_tree.delete(item)

        consultas = self.consulta_controller.get_by_patient(self.patient.id)
        for c in reversed(consultas):
            queixa = (c.queixa_principal[:40] + "...") if len(c.queixa_principal) > 40 else c.queixa_principal
            conduta = (c.conduta[:50] + "...") if len(c.conduta) > 50 else c.conduta
            peso = f"{c.peso_registrado}" if c.peso_registrado else "-"
            self.consultas_tree.insert("", 0, iid=c.id, values=(c.date.strftime("%d/%m/%Y"), queixa, conduta, peso))

    def _load_avaliacoes(self):
        for item in self.avaliacoes_tree.get_children():
            self.avaliacoes_tree.delete(item)

        avaliacoes = self.avaliacao_controller.get_by_patient(self.patient.id)
        for a in reversed(avaliacoes):
            imc = f"{a.calcular_imc()}" if a.calcular_imc() else "-"
            self.avaliacoes_tree.insert("", 0, iid=a.id, values=(
                a.date.strftime("%d/%m/%Y"),
                f"{a.peso}" if a.peso else "-",
                f"{a.altura}" if a.altura else "-",
                imc,
                f"{a.cintura}" if a.cintura else "-",
                f"{a.quadril}" if a.quadril else "-",
            ))

    def _load_planos(self):
        for item in self.planos_tree.get_children():
            self.planos_tree.delete(item)

        planos = self.plano_controller.get_by_patient(self.patient.id)
        for p in reversed(planos):
            self.planos_tree.insert("", 0, iid=p.id, values=(
                p.date.strftime("%d/%m/%Y"),
                f"{p.calorias}" if p.calorias else "-",
                f"{p.proteinas}" if p.proteinas else "-",
                f"{p.carboidratos}" if p.carboidratos else "-",
                f"{p.gorduras}" if p.gorduras else "-",
            ))

    def _load_resumo(self):
        self.resumo_text.delete("1.0", tk.END)

        anamnese = self.anamnese_controller.get_patient_anamnese(self.patient.id)
        consultas = self.consulta_controller.get_by_patient(self.patient.id)
        avaliacoes = self.avaliacao_controller.get_by_patient(self.patient.id)
        planos = self.plano_controller.get_by_patient(self.patient.id)

        ultima_avaliacao = avaliacoes[0] if avaliacoes else None

        texto = f"""
═══════════════════════════════════════════════════════════════
                           RESUMO DO PACIENTE
═══════════════════════════════════════════════════════════════

DADOS PESSOAIS
───────────────
Nome: {self.patient.name}
Telefone: {self.patient.phone or '-'}
E-mail: {self.patient.email or '-'}
Nascimento: {self.patient.birth_date.strftime('%d/%m/%Y') if self.patient.birth_date else '-'}

"""

        if anamnese:
            texto += f"""
ANAMNESE (Realizada em {anamnese.date.strftime('%d/%m/%Y')})
───────────────
Objetivo: {anamnese.objetivo_principal or '-'}
Peso máximo: {anamnese.peso_maximo or '-'} kg
Peso mínimo: {anamnese.peso_minimo or '-'} kg
Peso desejado: {anamnese.peso_desejado or '-'} kg
Alergias/Intolerâncias: {anamnese.alergio_intolerancias or '-'}

"""
        else:
            texto += "\nANAMNESE: Não realizada\n\n"

        if ultima_avaliacao:
            imc = ultima_avaliacao.calcular_imc()
            texto += f"""
ÚLTIMA AVALIAÇÃO ({ultima_avaliacao.date.strftime('%d/%m/%Y')})
───────────────
Peso: {ultima_avaliacao.peso or '-'} kg
Altura: {ultima_avaliacao.altura or '-'} cm
IMC: {f'{imc:.1f}' if imc else '-'}
Cintura: {ultima_avaliacao.cintura or '-'} cm
Quadril: {ultima_avaliacao.quadril or '-'} cm
PA: {ultima_avaliacao.pressao_sistolica or '-'}/{ultima_avaliacao.pressao_diastolica or '-'}
FC: {ultima_avaliacao.frequencia_cardiaca or '-'} bpm

"""
        else:
            texto += "\nAVALIAÇÕES: Nenhuma registrada\n\n"

        if consultas:
            ultima_consulta = consultas[0]
            texto += f"""
ÚLTIMA CONSULTA ({ultima_consulta.date.strftime('%d/%m/%Y')})
───────────────
Queixa: {ultima_consulta.queixa_principal or '-'}
Próximo retorno: {ultima_consulta.proximo_retorno.strftime('%d/%m/%Y') if ultima_consulta.proximo_retorno else 'Não agendado'}

"""

        texto += f"""
ESTATÍSTICAS
───────────────
Total de consultas: {len(consultas)}
Total de avaliações: {len(avaliacoes)}
Total de planos: {len(planos)}

═══════════════════════════════════════════════════════════════
"""
        self.resumo_text.insert("1.0", texto)

    def _nova_consulta(self):
        def on_save(consulta):
            try:
                self.consulta_controller.create(consulta)
                self._load_consultas()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Consulta registrada!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        from .consulta_window import ConsultaWindow
        ConsultaWindow(self, self.patient, on_save=on_save)

    def _editar_consulta(self):
        selection = self.consultas_tree.selection()
        if not selection:
            return
        consulta = self.consulta_controller.get_by_id(int(selection[0]))

        def on_save(c):
            try:
                self.consulta_controller.update(c)
                self._load_consultas()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Consulta atualizada!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        from .consulta_window import ConsultaWindow
        ConsultaWindow(self, self.patient, consulta=consulta, on_save=on_save)

    def _nova_avaliacao(self):
        def on_save(avaliacao):
            try:
                self.avaliacao_controller.create(avaliacao)
                self._load_avaliacoes()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Avaliação registrada!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        from .avaliacao_window import AvaliacaoWindow
        AvaliacaoWindow(self, self.patient, on_save=on_save)

    def _editar_avaliacao(self):
        selection = self.avaliacoes_tree.selection()
        if not selection:
            return
        avaliacao = self.avaliacao_controller.get_by_id(int(selection[0]))

        def on_save(a):
            try:
                self.avaliacao_controller.update(a)
                self._load_avaliacoes()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Avaliação atualizada!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        from .avaliacao_window import AvaliacaoWindow
        AvaliacaoWindow(self, self.patient, avaliacao=avaliacao, on_save=on_save)

    def _novo_plano(self):
        def on_save(plano):
            try:
                self.plano_controller.create(plano)
                self._load_planos()
                messagebox.showinfo("Sucesso", "Plano registrado!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        from .plano_alimentar_window import PlanoAlimentarWindow
        PlanoAlimentarWindow(self, self.patient, on_save=on_save)

    def _editar_plano(self):
        selection = self.planos_tree.selection()
        if not selection:
            return
        plano = self.plano_controller.get_by_id(int(selection[0]))

        def on_save(p):
            try:
                self.plano_controller.update(p)
                self._load_planos()
                messagebox.showinfo("Sucesso", "Plano atualizado!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        from .plano_alimentar_window import PlanoAlimentarWindow
        PlanoAlimentarWindow(self, self.patient, plano=plano, on_save=on_save)
