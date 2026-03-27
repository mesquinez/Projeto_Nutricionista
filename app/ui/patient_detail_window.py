import tkinter as tk
from copy import deepcopy
from typing import TYPE_CHECKING

from tkinter import messagebox, ttk

if TYPE_CHECKING:
    from ..controllers.anamnese_controller import AnamneseController
    from ..controllers.avaliacao_controller import AvaliacaoController
    from ..controllers.consulta_controller import ConsultaController
    from ..controllers.patient_controller import PatientController
    from ..controllers.plano_alimentar_controller import PlanoAlimentarController
    from ..models.patient import Patient


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
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_paciente = ttk.Frame(self.notebook)
        self.tab_consultas = ttk.Frame(self.notebook)
        self.tab_avaliacoes = ttk.Frame(self.notebook)
        self.tab_planos = ttk.Frame(self.notebook)
        self.tab_resumo = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_paciente, text="Paciente")
        self.notebook.add(self.tab_consultas, text="Consultas")
        self.notebook.add(self.tab_avaliacoes, text="Avaliacoes")
        self.notebook.add(self.tab_planos, text="Planos")
        self.notebook.add(self.tab_resumo, text="Resumo")

        self._create_paciente_tab()
        self._create_consultas_tab()
        self._create_avaliacoes_tab()
        self._create_planos_tab()
        self._create_resumo_tab()

        button_bar = ttk.Frame(self)
        button_bar.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_bar, text="Nova Anamnese", command=self._abrir_anamnese).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_bar, text="Fechar", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def _create_paciente_tab(self):
        frame = ttk.Frame(self.tab_paciente, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.LabelFrame(frame, text="Dados Cadastrais", padding=10)
        header.pack(fill=tk.X, pady=(0, 10))
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Nome:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)
        self.patient_name_value = ttk.Label(header, text="-")
        self.patient_name_value.grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(header, text="Telefone:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)
        self.patient_phone_value = ttk.Label(header, text="-")
        self.patient_phone_value.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(header, text="Nascimento:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=2)
        self.patient_birth_value = ttk.Label(header, text="-")
        self.patient_birth_value.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(header, text="Status:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=2)
        self.patient_status_value = ttk.Label(header, text="-")
        self.patient_status_value.grid(row=3, column=1, sticky="w", pady=2)

        actions = ttk.Frame(frame)
        actions.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(actions, text="Nova Anamnese", command=self._abrir_anamnese).pack(side=tk.LEFT)

        ttk.Label(frame, text="Anamneses Registradas").pack(anchor="w", pady=(0, 6))

        cols = ("date", "queixa")
        self.anamneses_tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        self.anamneses_tree.heading("date", text="Data")
        self.anamneses_tree.heading("queixa", text="Queixa Principal")
        self.anamneses_tree.column("date", width=120)
        self.anamneses_tree.column("queixa", width=620)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.anamneses_tree.yview)
        self.anamneses_tree.configure(yscrollcommand=scrollbar.set)

        self.anamneses_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_consultas_tab(self):
        frame = ttk.Frame(self.tab_consultas, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(anchor="w", pady=5)
        ttk.Button(btn_frame, text="+ Nova Consulta", command=self._nova_consulta).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Editar Selecionada", command=self._editar_consulta).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Excluir Selecionada", command=self._excluir_consulta).pack(side=tk.LEFT, padx=2)

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
        self.consultas_tree.bind("<Double-1>", lambda _e: self._editar_consulta())

    def _create_avaliacoes_tab(self):
        frame = ttk.Frame(self.tab_avaliacoes, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(anchor="w", pady=5)
        ttk.Button(btn_frame, text="+ Nova Avaliacao", command=self._nova_avaliacao).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Editar Selecionada", command=self._editar_avaliacao).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Excluir Selecionada", command=self._excluir_avaliacao).pack(side=tk.LEFT, padx=2)

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
        self.avaliacoes_tree.bind("<Double-1>", lambda _e: self._editar_avaliacao())

    def _create_planos_tab(self):
        frame = ttk.Frame(self.tab_planos, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(anchor="w", pady=5)
        ttk.Button(btn_frame, text="+ Novo Plano", command=self._novo_plano).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Editar Selecionado", command=self._editar_plano).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Excluir Selecionado", command=self._excluir_plano).pack(side=tk.LEFT, padx=2)

        cols = ("date", "calorias", "proteinas", "carboidratos", "gorduras")
        self.planos_tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        self.planos_tree.heading("date", text="Data")
        self.planos_tree.heading("calorias", text="Calorias")
        self.planos_tree.heading("proteinas", text="Proteinas")
        self.planos_tree.heading("carboidratos", text="Carboidratos")
        self.planos_tree.heading("gorduras", text="Gorduras")
        for col in cols:
            self.planos_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.planos_tree.yview)
        self.planos_tree.configure(yscrollcommand=scrollbar.set)

        self.planos_tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        self.planos_tree.bind("<Double-1>", lambda _e: self._editar_plano())

    def _create_resumo_tab(self):
        frame = ttk.Frame(self.tab_resumo, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        self.resumo_text = tk.Text(frame, wrap="word", font=("TkDefaultFont", 10))
        self.resumo_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.resumo_text.yview)
        self.resumo_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def _load_data(self):
        self._load_patient_summary()
        self._load_anamneses()
        self._load_consultas()
        self._load_avaliacoes()
        self._load_planos()
        self._load_resumo()

    def _load_patient_summary(self):
        birth_date = self.patient.birth_date.strftime("%d/%m/%Y") if self.patient.birth_date else "-"
        self.patient_name_value.config(text=self.patient.name or "-")
        self.patient_phone_value.config(text=self.patient.phone or "-")
        self.patient_birth_value.config(text=birth_date)
        self.patient_status_value.config(text=self.patient.status or "-")

    def _load_anamneses(self):
        for item in self.anamneses_tree.get_children():
            self.anamneses_tree.delete(item)

        anamneses = self.anamnese_controller.get_patient_anamnese_history(self.patient.id)
        for anamnese in reversed(anamneses):
            data = anamnese.data.strftime("%d/%m/%Y") if anamnese.data else "-"
            queixa = anamnese.queixa_principal or "-"
            if len(queixa) > 80:
                queixa = queixa[:80] + "..."
            self.anamneses_tree.insert("", 0, iid=f"anamnese-{anamnese.id}", values=(data, queixa))

    def _load_consultas(self):
        for item in self.consultas_tree.get_children():
            self.consultas_tree.delete(item)

        consultas = self.consulta_controller.get_by_patient(self.patient.id)
        for consulta in reversed(consultas):
            queixa = consulta.queixa_principal or ""
            conduta = consulta.conduta or ""
            if len(queixa) > 40:
                queixa = queixa[:40] + "..."
            if len(conduta) > 50:
                conduta = conduta[:50] + "..."
            peso = f"{consulta.peso_registrado}" if consulta.peso_registrado else "-"
            self.consultas_tree.insert("", 0, iid=consulta.id, values=(consulta.date.strftime("%d/%m/%Y"), queixa, conduta, peso))

    def _load_avaliacoes(self):
        for item in self.avaliacoes_tree.get_children():
            self.avaliacoes_tree.delete(item)

        avaliacoes = self.avaliacao_controller.get_by_patient(self.patient.id)
        for avaliacao in reversed(avaliacoes):
            imc = f"{avaliacao.calcular_imc()}" if avaliacao.calcular_imc() else "-"
            self.avaliacoes_tree.insert(
                "",
                0,
                iid=avaliacao.id,
                values=(
                    avaliacao.date.strftime("%d/%m/%Y"),
                    f"{avaliacao.peso}" if avaliacao.peso else "-",
                    f"{avaliacao.altura}" if avaliacao.altura else "-",
                    imc,
                    f"{avaliacao.cintura}" if avaliacao.cintura else "-",
                    f"{avaliacao.quadril}" if avaliacao.quadril else "-",
                ),
            )

    def _load_planos(self):
        for item in self.planos_tree.get_children():
            self.planos_tree.delete(item)

        planos = self.plano_controller.get_by_patient(self.patient.id)
        for plano in reversed(planos):
            self.planos_tree.insert(
                "",
                0,
                iid=plano.id,
                values=(
                    plano.date.strftime("%d/%m/%Y"),
                    f"{plano.calorias}" if plano.calorias else "-",
                    f"{plano.proteinas}" if plano.proteinas else "-",
                    f"{plano.carboidratos}" if plano.carboidratos else "-",
                    f"{plano.gorduras}" if plano.gorduras else "-",
                ),
            )

    def _load_resumo(self):
        self.resumo_text.config(state="normal")
        self.resumo_text.delete("1.0", tk.END)

        anamnese = self.anamnese_controller.get_patient_anamnese(self.patient.id)
        consultas = self.consulta_controller.get_by_patient(self.patient.id)
        avaliacoes = self.avaliacao_controller.get_by_patient(self.patient.id)
        planos = self.plano_controller.get_by_patient(self.patient.id)

        texto = f"""
RESUMO DO PACIENTE

Nome: {self.patient.name}
Telefone: {self.patient.phone or '-'}
E-mail: {self.patient.email or '-'}
Nascimento: {self.patient.birth_date.strftime('%d/%m/%Y') if self.patient.birth_date else '-'}

"""

        if anamnese:
            texto += f"""ANAMNESE ({anamnese.data.strftime('%d/%m/%Y') if anamnese.data else '-'})
Queixa principal: {anamnese.queixa_principal or '-'}
Objetivo: {anamnese.objetivo or '-'}
Historico de saude: {anamnese.historico_saude or '-'}
Alergias: {anamnese.alergias or '-'}

"""
        else:
            texto += "ANAMNESE: Nao realizada\n\n"

        if avaliacoes:
            ultima_avaliacao = avaliacoes[0]
            imc = ultima_avaliacao.calcular_imc()
            texto += f"""ULTIMA AVALIACAO ({ultima_avaliacao.date.strftime('%d/%m/%Y')})
Peso: {ultima_avaliacao.peso or '-'} kg
Altura: {ultima_avaliacao.altura or '-'} cm
IMC: {f'{imc:.1f}' if imc else '-'}
Cintura: {ultima_avaliacao.cintura or '-'} cm
Quadril: {ultima_avaliacao.quadril or '-'} cm
PA: {ultima_avaliacao.pressao_sistolica or '-'}/{ultima_avaliacao.pressao_diastolica or '-'}
FC: {ultima_avaliacao.frequencia_cardiaca or '-'} bpm

"""
        else:
            texto += "AVALIACOES: Nenhuma registrada\n\n"

        if consultas:
            ultima_consulta = consultas[0]
            texto += f"""ULTIMA CONSULTA ({ultima_consulta.date.strftime('%d/%m/%Y')})
Queixa: {ultima_consulta.queixa_principal or '-'}
Proximo retorno: {ultima_consulta.proximo_retorno.strftime('%d/%m/%Y') if ultima_consulta.proximo_retorno else 'Nao agendado'}

"""
        else:
            texto += "CONSULTAS: Nenhuma registrada\n\n"

        if planos:
            plano = planos[0]
            observacoes = plano.observacoes or "-"
            if len(observacoes) > 60:
                observacoes = observacoes[:60] + "..."
            texto += f"""PLANO ATUAL ({plano.date.strftime('%d/%m/%Y')})
Macros: {plano.calorias or '-'} kcal (P: {plano.proteinas or '-'}g, C: {plano.carboidratos or '-'}g, G: {plano.gorduras or '-'}g)
Obs: {observacoes}

"""

        texto += f"""ESTATISTICAS
Total de anamneses: {len(self.anamnese_controller.get_patient_anamnese_history(self.patient.id))}
Total de consultas: {len(consultas)}
Total de avaliacoes: {len(avaliacoes)}
Total de planos: {len(planos)}
"""

        self.resumo_text.insert("1.0", texto)
        self.resumo_text.config(state="disabled")

    def _abrir_anamnese(self):
        def on_save(anamnese):
            try:
                self.anamnese_controller.create_anamnese(anamnese)
                self._load_anamneses()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Anamnese salva!")
                return True
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .anamnese_window import AnamneseWindow

        AnamneseWindow(self, patient=self.patient, patients=[self.patient], on_save=on_save)

    def _nova_consulta(self):
        def on_save(consulta):
            try:
                self.consulta_controller.create(consulta)
                self._load_consultas()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Consulta registrada!")
                return True
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .consulta_window import ConsultaWindow

        ConsultaWindow(self, self.patient, on_save=on_save)

    def _editar_consulta(self):
        selection = self.consultas_tree.selection()
        if not selection:
            return
        consulta = self.consulta_controller.get_by_id(int(selection[0]))

        def on_save(consulta_atualizada):
            try:
                self.consulta_controller.update(consulta_atualizada)
                self._load_consultas()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Consulta atualizada!")
                return True
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .consulta_window import ConsultaWindow

        ConsultaWindow(self, self.patient, consulta=consulta, on_save=on_save)

    def _nova_avaliacao(self):
        def on_save(avaliacao):
            try:
                self.avaliacao_controller.create(avaliacao)
                self._load_avaliacoes()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Avaliacao registrada!")
                return True
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .avaliacao_window import AvaliacaoWindow

        AvaliacaoWindow(self, self.patient, on_save=on_save)

    def _editar_avaliacao(self):
        selection = self.avaliacoes_tree.selection()
        if not selection:
            return
        avaliacao = self.avaliacao_controller.get_by_id(int(selection[0]))

        def on_save(avaliacao_atualizada):
            try:
                self.avaliacao_controller.update(avaliacao_atualizada)
                self._load_avaliacoes()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Avaliacao atualizada!")
                return True
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .avaliacao_window import AvaliacaoWindow

        AvaliacaoWindow(self, self.patient, avaliacao=avaliacao, on_save=on_save)

    def _novo_plano(self):
        last_plano = self.plano_controller.get_last(self.patient.id)
        plano_to_pass = None

        if last_plano and messagebox.askyesno("Novo Plano", "Deseja carregar os dados do ultimo plano como base para este novo?"):
            plano_to_pass = deepcopy(last_plano)
            plano_to_pass.id = None
            from datetime import date

            plano_to_pass.date = date.today()

        def on_save(plano):
            try:
                self.plano_controller.create(plano)
                self._load_planos()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Plano registrado!")
                return True
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .plano_alimentar_window import PlanoAlimentarWindow

        PlanoAlimentarWindow(self, self.patient, plano=plano_to_pass, on_save=on_save)

    def _editar_plano(self):
        selection = self.planos_tree.selection()
        if not selection:
            return
        plano = self.plano_controller.get_by_id(int(selection[0]))

        def on_save(plano_atualizado):
            try:
                self.plano_controller.update(plano_atualizado)
                self._load_planos()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Plano atualizado!")
                return True
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .plano_alimentar_window import PlanoAlimentarWindow

        PlanoAlimentarWindow(self, self.patient, plano=plano, on_save=on_save)

    def _excluir_consulta(self):
        selection = self.consultas_tree.selection()
        if not selection:
            return
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta consulta?"):
            try:
                self.consulta_controller.delete(int(selection[0]))
                self._load_consultas()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Consulta excluida.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _excluir_avaliacao(self):
        selection = self.avaliacoes_tree.selection()
        if not selection:
            return
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta avaliacao?"):
            try:
                self.avaliacao_controller.delete(int(selection[0]))
                self._load_avaliacoes()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Avaliacao excluida.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _excluir_plano(self):
        selection = self.planos_tree.selection()
        if not selection:
            return
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este plano alimentar?"):
            try:
                self.plano_controller.delete(int(selection[0]))
                self._load_planos()
                self._load_resumo()
                messagebox.showinfo("Sucesso", "Plano excluido.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))
