import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.patient import Patient
    from ..models.avaliacao import Avaliacao

from app.ui.utils.formatters import format_date_br

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False


class AvaliacaoWindow(tk.Toplevel):
    def __init__(self, parent, patient: "Patient", avaliacao: Optional["Avaliacao"] = None, on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.patient = patient
        self.avaliacao = avaliacao
        self.on_save = on_save

        self.title("Avaliação Antroprométrica" if not avaliacao else "Editar Avaliação")
        self.geometry("550x650")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        if avaliacao:
            self._load_avaliacao_data()

    def _create_widgets(self):
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas, padding="15")

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        row = 0
        ttk.Label(frame, text="Data da Avaliação:", font=("", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5)
        row += 1
        if HAS_TKCALENDAR:
            self.date_picker = DateEntry(frame, width=33, date_pattern="dd/mm/yyyy")
            self.date_picker.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        else:
            self.date_entry = ttk.Entry(frame, width=35)
            self.date_entry.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
            ttk.Label(frame, text="(DD/MM/AAAA)").grid(row=row, column=2, sticky="w", padx=5)
            self.date_entry.bind("<KeyRelease>", self._on_date_change)
            self.date_entry.bind("<Return>", lambda e: self.peso_entry.focus_set())
        row += 1

        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=4, sticky="ew", pady=10)
        ttk.Label(frame, text="MEDIDAS BÁSICAS", font=("", 10, "bold")).grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        fields_basic = [
            ("Peso (kg):", "peso_entry"),
            ("Altura (cm):", "altura_entry"),
        ]
        for label, attr in fields_basic:
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(frame, width=15)
            entry.grid(row=row, column=1, sticky="w", pady=3)
            entry.bind("<Return>", lambda e: self._save())
            setattr(self, attr, entry)
            row += 1

        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=4, sticky="ew", pady=10)
        ttk.Label(frame, text="CIRCUNFERÊNCIAS (cm)", font=("", 10, "bold")).grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        fields_circ = [
            ("Cintura:", "cintura_entry"),
            ("Quadril:", "quadril_entry"),
            ("Braço Dir.:", "bracod_entry"),
            ("Braço Esq.:", "bracoe_entry"),
            ("Coxa:", "coxa_entry"),
            ("Panturrilha:", "panturrilha_entry"),
            ("Pescoço:", "pescoco_entry"),
        ]
        for i, (label, attr) in enumerate(fields_circ):
            col = 0 if i % 2 == 0 else 2
            if i > 0 and i % 2 == 0:
                row += 1
            ttk.Label(frame, text=label).grid(row=row, column=col, sticky="w", pady=3)
            entry = ttk.Entry(frame, width=15)
            entry.grid(row=row, column=col+1, sticky="w", pady=3)
            entry.bind("<Return>", lambda e: self._save())
            setattr(self, attr, entry)

        ttk.Separator(frame, orient="horizontal").grid(row=row+1, column=0, columnspan=4, sticky="ew", pady=10)
        ttk.Label(frame, text="SINAIS VITAIS", font=("", 10, "bold")).grid(row=row+1, column=0, columnspan=4, sticky="w")
        row += 2

        fields_vitals = [
            ("PA Sistólica:", "pa_sis_entry"),
            ("PA Diastólica:", "pa_dia_entry"),
            ("FC (bpm):", "fc_entry"),
        ]
        for i, (label, attr) in enumerate(fields_vitals):
            col = 0 if i % 2 == 0 else 2
            if i > 0 and i % 2 == 0:
                row += 1
            ttk.Label(frame, text=label).grid(row=row, column=col, sticky="w", pady=3)
            entry = ttk.Entry(frame, width=15)
            entry.grid(row=row, column=col+1, sticky="w", pady=3)
            entry.bind("<Return>", lambda e: self._save())
            setattr(self, attr, entry)

        ttk.Separator(frame, orient="horizontal").grid(row=row+1, column=0, columnspan=4, sticky="ew", pady=10)
        ttk.Label(frame, text="OBSERVAÇÕES", font=("", 10, "bold")).grid(row=row+1, column=0, columnspan=4, sticky="w")
        row += 2

        self.observacoes_text = tk.Text(frame, width=55, height=4)
        self.observacoes_text.grid(row=row, column=0, columnspan=4, sticky="ew", pady=5)
        row += 1

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=row, column=0, columnspan=4, pady=20)
        ttk.Button(button_frame, text="Salvar", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)

        if HAS_TKCALENDAR:
            self.date_picker.focus_set()
        else:
            self.date_entry.focus_set()

    def _load_avaliacao_data(self):
        a = self.avaliacao
        if HAS_TKCALENDAR:
            self.date_picker.set_date(a.date)
        else:
            self.date_entry.insert(0, a.date.isoformat())
        
        self._set_float(self.peso_entry, a.peso)
        self._set_float(self.altura_entry, a.altura)
        self._set_float(self.cintura_entry, a.cintura)
        self._set_float(self.quadril_entry, a.quadril)
        self._set_float(self.bracod_entry, a.bracodireito)
        self._set_float(self.bracoe_entry, a.bracoesquedo)
        self._set_float(self.coxa_entry, a.coxa)
        self._set_float(self.panturrilha_entry, a.panturrilha)
        self._set_float(self.pescoco_entry, a.pescoco)
        self._set_int(self.pa_sis_entry, a.pressao_sistolica)
        self._set_int(self.pa_dia_entry, a.pressao_diastolica)
        self._set_int(self.fc_entry, a.frequencia_cardiaca)
        self.observacoes_text.insert("1.0", a.observacoes or "")

    def _set_float(self, entry: ttk.Entry, val):
        if val is not None:
            entry.insert(0, str(val))

    def _set_int(self, entry: ttk.Entry, val):
        if val is not None:
            entry.insert(0, str(val))

    def _on_date_change(self, event=None):
        if not HAS_TKCALENDAR:
            formatted = format_date_br(self.date_entry.get())
            current_pos = self.date_entry.index(tk.INSERT)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, formatted)
            self.date_entry.icursor(current_pos)



    def _save(self):
        from ..models.avaliacao import Avaliacao
        from ..utils.validators import is_valid_number
        from ..utils.converters import coerce_date_or_none
        
        # Validação de formato antes de instanciar o modelo
        num_fields = [
            (self.peso_entry, "Peso"), (self.altura_entry, "Altura"),
            (self.cintura_entry, "Cintura"), (self.quadril_entry, "Quadril"),
            (self.bracod_entry, "Braço Direito"), (self.bracoe_entry, "Braço Esquerdo"),
            (self.coxa_entry, "Coxa"), (self.panturrilha_entry, "Panturrilha"),
            (self.pescoco_entry, "Pescoço"), (self.pa_sis_entry, "PA Sistólica"),
            (self.pa_dia_entry, "PA Diastólica"), (self.fc_entry, "FC (bpm)")
        ]
        
        errors = []
        for entry, name in num_fields:
            if not is_valid_number(entry.get().strip()):
                errors.append(f"Formato inválido para o campo '{name}'.")
        
        if not HAS_TKCALENDAR:
            d_txt = self.date_entry.get().strip()
            if d_txt and not coerce_date_or_none(d_txt):
                errors.append("Formato de data inválido (use AAAA-MM-DD).")

        if errors:
            messagebox.showerror("Erro de Preenchimento", "\n".join(errors))
            return

        avaliacao = Avaliacao(
            id=self.avaliacao.id if self.avaliacao else None,
            patient_id=self.patient.id,
            date=self._get_date(),
            peso=self.peso_entry.get().strip() or None,
            altura=self.altura_entry.get().strip() or None,
            cintura=self.cintura_entry.get().strip() or None,
            quadril=self.quadril_entry.get().strip() or None,
            bracodireito=self.bracod_entry.get().strip() or None,
            bracoesquedo=self.bracoe_entry.get().strip() or None,
            coxa=self.coxa_entry.get().strip() or None,
            panturrilha=self.panturrilha_entry.get().strip() or None,
            pescoco=self.pescoco_entry.get().strip() or None,
            pressao_sistolica=self.pa_sis_entry.get().strip() or None,
            pressao_diastolica=self.pa_dia_entry.get().strip() or None,
            frequencia_cardiaca=self.fc_entry.get().strip() or None,
            observacoes=self.observacoes_text.get("1.0", tk.END).strip(),
        )

        if self.on_save:
            success = self.on_save(avaliacao)
            if not success:
                return # abort window kill
        self.destroy()

    def _get_date(self) -> date:
        from ..utils.converters import coerce_date_or_today
        if HAS_TKCALENDAR:
            d = self.date_picker.get_date()
            return d if isinstance(d, date) else date.today()
        else:
            d = self.date_entry.get().strip()
            # Tentar converter DD/MM/AAAA para ISO se necessário
            from ..utils.converters import coerce_date_or_today
            if "/" in d:
                try: 
                    parts = d.split("/")
                    d = f"{parts[2]}-{parts[1]}-{parts[0]}"
                except: pass
            return coerce_date_or_today(d)
