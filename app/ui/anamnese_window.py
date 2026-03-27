import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Callable, Optional

from app.ui.utils.formatters import format_date_br

if TYPE_CHECKING:
    from ..models.anamnese import Anamnese
    from ..models.patient import Patient

try:
    from tkcalendar import DateEntry

    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False


class AnamneseWindow(tk.Toplevel):
    def __init__(
        self,
        parent,
        patient: Optional["Patient"] = None,
        patients: Optional[list["Patient"]] = None,
        anamnese: Optional["Anamnese"] = None,
        on_save: Optional[Callable] = None,
    ):
        super().__init__(parent)
        self.patient = patient
        self.patients = patients or ([patient] if patient else [])
        self.anamnese = anamnese
        self.on_save = on_save
        self.result = None
        self.selected_patient = patient
        self.patient_options = {}

        self.title("Anamnese" if not anamnese else "Editar Anamnese")
        self.geometry("760x760")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        if anamnese:
            self._load_anamnese_data()

    def _create_widgets(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(1, weight=1)

        ttk.Label(container, text="Paciente:").grid(row=0, column=0, sticky="nw", pady=4, padx=(0, 10))
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(container, textvariable=self.patient_var, state="readonly")
        self.patient_combo.grid(row=0, column=1, sticky="ew", pady=4)
        self.patient_combo.bind("<<ComboboxSelected>>", self._on_patient_selected)

        resumo_frame = ttk.LabelFrame(container, text="Resumo do Paciente", padding=10)
        resumo_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 12))
        resumo_frame.columnconfigure(1, weight=1)

        ttk.Label(resumo_frame, text="Nome:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)
        self.patient_name_value = ttk.Label(resumo_frame, text="-")
        self.patient_name_value.grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(resumo_frame, text="Data de nascimento:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)
        self.patient_birth_value = ttk.Label(resumo_frame, text="-")
        self.patient_birth_value.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(resumo_frame, text="Telefone:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=2)
        self.patient_phone_value = ttk.Label(resumo_frame, text="-")
        self.patient_phone_value.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(resumo_frame, text="Status:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=2)
        self.patient_status_value = ttk.Label(resumo_frame, text="-")
        self.patient_status_value.grid(row=3, column=1, sticky="w", pady=2)

        self._load_patient_options()

        ttk.Label(container, text="Data:").grid(row=2, column=0, sticky="nw", pady=4, padx=(0, 10))
        if HAS_TKCALENDAR:
            self.data_picker = DateEntry(container, width=18, date_pattern="dd/mm/yyyy")
            self.data_picker.grid(row=2, column=1, sticky="w", pady=4)
        else:
            self.data_entry = ttk.Entry(container, width=20)
            self.data_entry.grid(row=2, column=1, sticky="w", pady=4)
            self.data_entry.bind("<KeyRelease>", self._on_date_change)

        self.text_fields = {}
        fields = [
            ("queixa_principal", "Queixa principal:", 4),
            ("objetivo", "Objetivo:", 4),
            ("historico_saude", "Histórico de saúde:", 4),
            ("medicamentos", "Medicamentos:", 3),
            ("alergias", "Alergias:", 3),
            ("habitos_alimentares", "Hábitos alimentares:", 4),
            ("ingestao_agua", "Ingestão de água:", 3),
            ("rotina", "Rotina:", 4),
            ("sono", "Sono:", 3),
            ("atividade_fisica", "Atividade física:", 3),
            ("funcionamento_intestinal", "Funcionamento intestinal:", 3),
            ("alcool", "Álcool:", 3),
            ("tabagismo", "Tabagismo:", 3),
            ("observacoes", "Observações:", 4),
        ]

        row = 3
        for field_name, label, height in fields:
            ttk.Label(container, text=label).grid(row=row, column=0, sticky="nw", pady=4, padx=(0, 10))
            text = tk.Text(container, height=height, wrap="word")
            text.grid(row=row, column=1, sticky="nsew", pady=4)
            container.rowconfigure(row, weight=1)
            self.text_fields[field_name] = text
            row += 1

        button_frame = ttk.Frame(container)
        button_frame.grid(row=row, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(button_frame, text="Salvar", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.patient_combo.focus_set()

    def _load_patient_options(self):
        values = []
        for patient in self.patients:
            if not patient or patient.id is None:
                continue
            label = f"{patient.id} - {patient.name}"
            self.patient_options[label] = patient
            values.append(label)

        self.patient_combo["values"] = values

        if self.patient and self.patient.id is not None:
            selected_label = f"{self.patient.id} - {self.patient.name}"
            if selected_label in self.patient_options:
                self.patient_var.set(selected_label)
                self.selected_patient = self.patient_options[selected_label]
        elif values:
            self.patient_var.set(values[0])
            self.selected_patient = self.patient_options[values[0]]

        self._update_patient_summary()

    def _on_patient_selected(self, _event=None):
        self.selected_patient = self.patient_options.get(self.patient_var.get())
        self._update_patient_summary()

    def _update_patient_summary(self):
        patient = self.selected_patient
        if not patient:
            self.patient_name_value.config(text="-")
            self.patient_birth_value.config(text="-")
            self.patient_phone_value.config(text="-")
            self.patient_status_value.config(text="-")
            return

        birth_date = patient.birth_date.strftime("%d/%m/%Y") if patient.birth_date else "-"
        self.patient_name_value.config(text=patient.name or "-")
        self.patient_birth_value.config(text=birth_date)
        self.patient_phone_value.config(text=patient.phone or "-")
        self.patient_status_value.config(text=patient.status or "-")

    def _load_anamnese_data(self):
        anamnese = self.anamnese
        if HAS_TKCALENDAR:
            self.data_picker.set_date(anamnese.data)
        else:
            self.data_entry.insert(0, anamnese.data.strftime("%d/%m/%Y"))

        for field_name, widget in self.text_fields.items():
            widget.insert("1.0", getattr(anamnese, field_name, "") or "")

    def _on_date_change(self, _event=None):
        if HAS_TKCALENDAR:
            return

        formatted = format_date_br(self.data_entry.get())
        current_pos = self.data_entry.index(tk.INSERT)
        self.data_entry.delete(0, tk.END)
        self.data_entry.insert(0, formatted)
        self.data_entry.icursor(current_pos)

    def _get_data(self) -> date:
        if HAS_TKCALENDAR:
            value = self.data_picker.get_date()
            return value if isinstance(value, date) else date.today()

        raw = self.data_entry.get().strip()
        if not raw:
            return None
        try:
            day, month, year = raw.split("/")
            return date(int(year), int(month), int(day))
        except Exception:
            return None

    def _save(self):
        from ..models.anamnese import Anamnese

        selected_patient = self.selected_patient or self.patient_options.get(self.patient_var.get())
        if not selected_patient:
            messagebox.showerror("Erro", "Selecione um paciente.")
            return

        data_value = self._get_data()
        if not data_value:
            messagebox.showerror("Erro", "Data inválida. Use DD/MM/AAAA.")
            return

        anamnese = Anamnese(
            id=self.anamnese.id if self.anamnese else None,
            patient_id=selected_patient.id,
            data=data_value,
            queixa_principal=self.text_fields["queixa_principal"].get("1.0", tk.END).strip(),
            objetivo=self.text_fields["objetivo"].get("1.0", tk.END).strip(),
            historico_saude=self.text_fields["historico_saude"].get("1.0", tk.END).strip(),
            medicamentos=self.text_fields["medicamentos"].get("1.0", tk.END).strip(),
            alergias=self.text_fields["alergias"].get("1.0", tk.END).strip(),
            habitos_alimentares=self.text_fields["habitos_alimentares"].get("1.0", tk.END).strip(),
            ingestao_agua=self.text_fields["ingestao_agua"].get("1.0", tk.END).strip(),
            rotina=self.text_fields["rotina"].get("1.0", tk.END).strip(),
            sono=self.text_fields["sono"].get("1.0", tk.END).strip(),
            atividade_fisica=self.text_fields["atividade_fisica"].get("1.0", tk.END).strip(),
            funcionamento_intestinal=self.text_fields["funcionamento_intestinal"].get("1.0", tk.END).strip(),
            alcool=self.text_fields["alcool"].get("1.0", tk.END).strip(),
            tabagismo=self.text_fields["tabagismo"].get("1.0", tk.END).strip(),
            observacoes=self.text_fields["observacoes"].get("1.0", tk.END).strip(),
        )

        self.result = anamnese
        if self.on_save:
            success = self.on_save(anamnese)
            if not success:
                return
        self.destroy()

    def get_result(self) -> Optional["Anamnese"]:
        return self.result
