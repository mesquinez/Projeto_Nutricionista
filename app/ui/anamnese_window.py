import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.patient import Patient
    from ..models.anamnese import Anamnese
    from ..controllers.anamnese_controller import AnamneseController

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False


class AnamneseWindow(tk.Toplevel):
    def __init__(
        self,
        parent,
        patient: "Patient",
        anamnese: Optional["Anamnese"] = None,
        on_save: Optional[Callable] = None,
    ):
        super().__init__(parent)
        self.patient = patient
        self.anamnese = anamnese
        self.on_save = on_save
        self.result = None

        self.title("Anamnese Nutricional" if not anamnese else "Editar Anamnese")
        self.geometry("750x700")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        if anamnese:
            self._load_anamnese_data()

    def _create_widgets(self):
        main_canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas, padding="10")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        row = 0
        self._create_section_title(scrollable_frame, "OBJETIVO PRINCIPAL", row)
        row += 1
        self.objetivo_entry = ttk.Entry(scrollable_frame, width=80)
        self.objetivo_entry.grid(row=row, column=0, columnspan=2, sticky="ew", pady=2)
        self.objetivo_entry.bind("<Return>", lambda e: self._save())
        row += 1

        self._create_section_title(scrollable_frame, "HISTÓRICO DE PESO", row)
        row += 1
        ttk.Label(scrollable_frame, text="Peso máximo (kg):").grid(row=row, column=0, sticky="w", pady=2)
        self.peso_max_entry = ttk.Entry(scrollable_frame, width=20)
        self.peso_max_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.peso_max_entry.bind("<Return>", lambda e: self._save())
        row += 1
        ttk.Label(scrollable_frame, text="Peso mínimo (kg):").grid(row=row, column=0, sticky="w", pady=2)
        self.peso_min_entry = ttk.Entry(scrollable_frame, width=20)
        self.peso_min_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.peso_min_entry.bind("<Return>", lambda e: self._save())
        row += 1
        ttk.Label(scrollable_frame, text="Peso desejado (kg):").grid(row=row, column=0, sticky="w", pady=2)
        self.peso_desejado_entry = ttk.Entry(scrollable_frame, width=20)
        self.peso_desejado_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.peso_desejado_entry.bind("<Return>", lambda e: self._save())
        row += 1

        self._create_section_title(scrollable_frame, "ATIVIDADE FÍSICA", row)
        row += 1
        ttk.Label(scrollable_frame, text="Pratica atividade física?").grid(row=row, column=0, sticky="w", pady=2)
        self.atividade_entry = ttk.Entry(scrollable_frame, width=60)
        self.atividade_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.atividade_entry.bind("<Return>", lambda e: self._save())
        row += 1
        ttk.Label(scrollable_frame, text="Frequência:").grid(row=row, column=0, sticky="w", pady=2)
        self.frequencia_entry = ttk.Entry(scrollable_frame, width=60)
        self.frequencia_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.frequencia_entry.bind("<Return>", lambda e: self._save())
        row += 1
        ttk.Label(scrollable_frame, text="Duração por sessão:").grid(row=row, column=0, sticky="w", pady=2)
        self.tempo_entry = ttk.Entry(scrollable_frame, width=60)
        self.tempo_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.tempo_entry.bind("<Return>", lambda e: self._save())
        row += 1

        self._create_section_title(scrollable_frame, "SONO", row)
        row += 1
        ttk.Label(scrollable_frame, text="Qualidade do sono:").grid(row=row, column=0, sticky="w", pady=2)
        self.sono_qualidade_entry = ttk.Combobox(
            scrollable_frame, width=58,
            values=["Bom", "Regular", "Ruim", "Insônia"],
            state="readonly"
        )
        self.sono_qualidade_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Horas de sono por noite:").grid(row=row, column=0, sticky="w", pady=2)
        self.sono_horas_entry = ttk.Combobox(
            scrollable_frame, width=58,
            values=["Menos de 5h", "5-6h", "6-7h", "7-8h", "Mais de 8h"],
            state="readonly"
        )
        self.sono_horas_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._create_section_title(scrollable_frame, "HÁBITOS ALIMENTARES", row)
        row += 1
        ttk.Label(scrollable_frame, text="Descreva seus hábitos alimentares:").grid(row=row, column=0, sticky="w", pady=2)
        row += 1
        self.habitos_text = tk.Text(scrollable_frame, width=60, height=3)
        self.habitos_text.grid(row=row, column=0, columnspan=2, sticky="ew", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Refeições por dia:").grid(row=row, column=0, sticky="w", pady=2)
        self.refeicoes_combo = ttk.Combobox(
            scrollable_frame, width=58,
            values=["1", "2", "3", "4", "5", "6 ou mais"],
            state="readonly"
        )
        self.refeicoes_combo.grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Horários das refeições:").grid(row=row, column=0, sticky="w", pady=2)
        self.horarios_entry = ttk.Entry(scrollable_frame, width=60)
        self.horarios_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.horarios_entry.bind("<Return>", lambda e: self._save())
        row += 1

        self._create_section_title(scrollable_frame, "PREFERÊNCIAS ALIMENTARES", row)
        row += 1
        ttk.Label(scrollable_frame, text="Alimentos preferidos:").grid(row=row, column=0, sticky="w", pady=2)
        self.preferencias_entry = ttk.Entry(scrollable_frame, width=60)
        self.preferencias_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.preferencias_entry.bind("<Return>", lambda e: self._save())
        row += 1
        ttk.Label(scrollable_frame, text="Alimentos que não gosta:").grid(row=row, column=0, sticky="w", pady=2)
        self.aversoes_entry = ttk.Entry(scrollable_frame, width=60)
        self.aversoes_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.aversoes_entry.bind("<Return>", lambda e: self._save())
        row += 1
        ttk.Label(scrollable_frame, text="Alergias/Intolerâncias:").grid(row=row, column=0, sticky="w", pady=2)
        self.alergias_entry = ttk.Entry(scrollable_frame, width=60)
        self.alergias_entry.grid(row=row, column=1, sticky="w", pady=2)
        self.alergias_entry.bind("<Return>", lambda e: self._save())
        row += 1

        self._create_section_title(scrollable_frame, "INGESTÃO DE LÍQUIDOS", row)
        row += 1
        ttk.Label(scrollable_frame, text="Consumo de água diário:").grid(row=row, column=0, sticky="w", pady=2)
        self.agua_entry = ttk.Combobox(
            scrollable_frame, width=58,
            values=["Menos de 1L", "1-2L", "2-3L", "Mais de 3L"],
            state="readonly"
        )
        self.agua_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Consumo de álcool:").grid(row=row, column=0, sticky="w", pady=2)
        self.alcool_entry = ttk.Combobox(
            scrollable_frame, width=58,
            values=["Não bebe", "Ocasionalmente", "Fins de semana", "Diariamente"],
            state="readonly"
        )
        self.alcool_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Consumo de cigarro:").grid(row=row, column=0, sticky="w", pady=2)
        self.cigarro_entry = ttk.Combobox(
            scrollable_frame, width=58,
            values=["Não fuma", "Menos de 5/dia", "5-10/dia", "Mais de 10/dia"],
            state="readonly"
        )
        self.cigarro_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._create_section_title(scrollable_frame, "HISTÓRICO DE SAÚDE", row)
        row += 1
        ttk.Label(scrollable_frame, text="Doenças prévias:").grid(row=row, column=0, sticky="w", pady=2)
        self.doencas_prev_entry = ttk.Entry(scrollable_frame, width=60)
        self.doencas_prev_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Doenças familiares:").grid(row=row, column=0, sticky="w", pady=2)
        self.doencas_fam_entry = ttk.Entry(scrollable_frame, width=60)
        self.doencas_fam_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Medicamentos em uso:").grid(row=row, column=0, sticky="w", pady=2)
        self.medicamentos_entry = ttk.Entry(scrollable_frame, width=60)
        self.medicamentos_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Suplementação:").grid(row=row, column=0, sticky="w", pady=2)
        self.suplementacao_entry = ttk.Entry(scrollable_frame, width=60)
        self.suplementacao_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Cirurgias realizadas:").grid(row=row, column=0, sticky="w", pady=2)
        self.cirurgias_entry = ttk.Entry(scrollable_frame, width=60)
        self.cirurgias_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        ttk.Label(scrollable_frame, text="Internações:").grid(row=row, column=0, sticky="w", pady=2)
        self.internacoes_entry = ttk.Entry(scrollable_frame, width=60)
        self.internacoes_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._create_section_title(scrollable_frame, "FUNÇÕES BIOLÓGICAS", row)
        row += 1
        ttk.Label(scrollable_frame, text="Ritmo intestinal:").grid(row=row, column=0, sticky="w", pady=2)
        self.ritmo_entry = ttk.Combobox(
            scrollable_frame, width=58,
            values=["Regular", "Irregular", "Constipação", "Diarreia"],
            state="readonly"
        )
        self.ritmo_entry.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        self._create_section_title(scrollable_frame, "OBSERVAÇÕES", row)
        row += 1
        self.observacoes_text = tk.Text(scrollable_frame, width=60, height=4)
        self.observacoes_text.grid(row=row, column=0, columnspan=2, sticky="ew", pady=2)
        row += 1

        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Salvar", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.objetivo_entry.focus_set()

    def _create_section_title(self, parent, title: str, row: int):
        ttk.Separator(parent, orient="horizontal").grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=(10, 5)
        )
        ttk.Label(parent, text=title, font=("TkDefaultFont", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(5, 2)
        )

    def _load_anamnese_data(self):
        a = self.anamnese
        self.objetivo_entry.insert(0, a.objetivo_principal or "")
        self.peso_max_entry.insert(0, str(a.peso_maximo) if a.peso_maximo else "")
        self.peso_min_entry.insert(0, str(a.peso_minimo) if a.peso_minimo else "")
        self.peso_desejado_entry.insert(0, str(a.peso_desejado) if a.peso_desejado else "")
        self.atividade_entry.insert(0, a.atividade_fisica or "")
        self.frequencia_entry.insert(0, a.frequencia_atividade or "")
        self.tempo_entry.insert(0, a.tempo_atividade or "")
        self._set_combo(self.sono_qualidade_entry, a.sono_qualidade)
        self._set_combo(self.sono_horas_entry, a.sono_horas)
        self.habitos_text.insert("1.0", a.habitos_alimentares or "")
        self._set_combo(self.refeicoes_combo, str(a.refeicoes_dia) if a.refeicoes_dia else "")
        self.horarios_entry.insert(0, a.horarios_refeicoes or "")
        self.preferencias_entry.insert(0, a.preferencia_alimentar or "")
        self.aversoes_entry.insert(0, a.aversao_alimentar or "")
        self.alergias_entry.insert(0, a.alergio_intolerancias or "")
        self._set_combo(self.agua_entry, a.consumo_agua)
        self._set_combo(self.alcool_entry, a.consumo_alcool)
        self._set_combo(self.cigarro_entry, a.consumo_cigarro)
        self.doencas_prev_entry.insert(0, a.doencas_previas or "")
        self.doencas_fam_entry.insert(0, a.doencas_familiares or "")
        self.medicamentos_entry.insert(0, a.medicamentos or "")
        self.suplementacao_entry.insert(0, a.suplementacao or "")
        self.cirurgias_entry.insert(0, a.cirurgias or "")
        self.internacoes_entry.insert(0, a.internacoes or "")
        self._set_combo(self.ritmo_entry, a.ritmo_intestinal)
        self.observacoes_text.insert("1.0", a.observacoes_gerais or "")

    def _set_combo(self, combo: ttk.Combobox, value: str):
        if value:
            combo.set(value)



    def _save(self):
        from ..models.anamnese import Anamnese
        from ..utils.validators import is_valid_number
        
        errors = []
        if not is_valid_number(self.peso_max_entry.get().strip()):
            errors.append("Peso Máximo deve ser um número.")
        if not is_valid_number(self.peso_min_entry.get().strip()):
            errors.append("Peso Mínimo deve ser um número.")
        if not is_valid_number(self.peso_desejado_entry.get().strip()):
            errors.append("Peso Desejado deve ser um número.")
            
        if errors:
            messagebox.showerror("Erro de Formato", "\n".join(errors))
            return

        anamnese = Anamnese(
            id=self.anamnese.id if self.anamnese else None,
            patient_id=self.patient.id,
            date=self.anamnese.date if self.anamnese else date.today(),
            objetivo_principal=self.objetivo_entry.get().strip(),
            peso_maximo=self.peso_max_entry.get().strip() or None,
            peso_minimo=self.peso_min_entry.get().strip() or None,
            peso_desejado=self.peso_desejado_entry.get().strip() or None,
            atividade_fisica=self.atividade_entry.get().strip(),
            frequencia_atividade=self.frequencia_entry.get().strip(),
            tempo_atividade=self.tempo_entry.get().strip(),
            sono_qualidade=self.sono_qualidade_entry.get().strip(),
            sono_horas=self.sono_horas_entry.get().strip(),
            habitos_alimentares=self.habitos_text.get("1.0", tk.END).strip(),
            refeicoes_dia=self.refeicoes_combo.get().strip() or None,
            horarios_refeicoes=self.horarios_entry.get().strip(),
            preferencia_alimentar=self.preferencias_entry.get().strip(),
            aversao_alimentar=self.aversoes_entry.get().strip(),
            alergio_intolerancias=self.alergias_entry.get().strip(),
            consumo_agua=self.agua_entry.get().strip(),
            consumo_alcool=self.alcool_entry.get().strip(),
            consumo_cigarro=self.cigarro_entry.get().strip(),
            doencas_previas=self.doencas_prev_entry.get().strip(),
            doencas_familiares=self.doencas_fam_entry.get().strip(),
            medicamentos=self.medicamentos_entry.get().strip(),
            suplementacao=self.suplementacao_entry.get().strip(),
            cirurgias=self.cirurgias_entry.get().strip(),
            internacoes=self.internacoes_entry.get().strip(),
            ritmo_intestinal=self.ritmo_entry.get().strip(),
            observacoes_gerais=self.observacoes_text.get("1.0", tk.END).strip(),
        )

        self.result = anamnese
        if self.on_save:
            success = self.on_save(anamnese)
            if not success:
                return # protect text fields
        self.destroy()

    def get_result(self) -> Optional["Anamnese"]:
        return self.result
