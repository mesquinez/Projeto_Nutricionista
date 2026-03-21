import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.patient import Patient
    from ..models.consulta import Consulta

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False


class ConsultaWindow(tk.Toplevel):
    def __init__(self, parent, patient: "Patient", consulta: Optional["Consulta"] = None, on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.patient = patient
        self.consulta = consulta
        self.on_save = on_save

        self.title("Registrar Consulta" if not consulta else "Editar Consulta")
        self.geometry("600x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        if consulta:
            self._load_consulta_data()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        row = 0
        ttk.Label(main_frame, text="Data:", font=("", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5)
        row += 1
        
        if HAS_TKCALENDAR:
            self.date_picker = DateEntry(main_frame, width=33, date_pattern="dd/mm/yyyy")
            self.date_picker.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        else:
            self.date_entry = ttk.Entry(main_frame, width=35)
            self.date_entry.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        ttk.Separator(main_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1

        ttk.Label(main_frame, text="QUEIXA PRINCIPAL", font=("", 10, "bold")).grid(row=row, column=0, sticky="w")
        row += 1
        self.queixa_text = tk.Text(main_frame, width=60, height=4)
        self.queixa_text.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        row += 1

        ttk.Label(main_frame, text="OBSERVAÇÕES DA CONSULTA", font=("", 10, "bold")).grid(row=row, column=0, sticky="w")
        row += 1
        self.observacoes_text = tk.Text(main_frame, width=60, height=5)
        self.observacoes_text.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        row += 1

        ttk.Separator(main_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1

        ttk.Label(main_frame, text="CONDUTA / ORIENTAÇÕES", font=("", 10, "bold")).grid(row=row, column=0, sticky="w")
        row += 1
        self.conduta_text = tk.Text(main_frame, width=60, height=5)
        self.conduta_text.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        row += 1

        ttk.Label(main_frame, text="Próximo Retorno:").grid(row=row, column=0, sticky="w", pady=5)
        if HAS_TKCALENDAR:
            self.retorno_picker = DateEntry(main_frame, width=33, date_pattern="dd/mm/yyyy")
            self.retorno_picker.grid(row=row, column=1, sticky="w", pady=5)
        else:
            self.retorno_entry = ttk.Entry(main_frame, width=35)
            self.retorno_entry.grid(row=row, column=1, sticky="w", pady=5)
        row += 1

        ttk.Label(main_frame, text="Peso registrado (kg):").grid(row=row, column=0, sticky="w", pady=5)
        self.peso_entry = ttk.Entry(main_frame, width=20)
        self.peso_entry.grid(row=row, column=1, sticky="w", pady=5)
        row += 1

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Salvar", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _load_consulta_data(self):
        c = self.consulta
        if HAS_TKCALENDAR:
            self.date_picker.set_date(c.date)
            if c.proximo_retorno:
                self.retorno_picker.set_date(c.proximo_retorno)
        else:
            self.date_entry.insert(0, c.date.isoformat())
            if c.proximo_retorno:
                self.retorno_entry.insert(0, c.proximo_retorno.isoformat())
        self.queixa_text.insert("1.0", c.queixa_principal or "")
        self.observacoes_text.insert("1.0", c.observacoes or "")
        self.conduta_text.insert("1.0", c.conduta or "")
        if c.peso_registrado:
            self.peso_entry.insert(0, str(c.peso_registrado))

    def _get_float(self, entry: ttk.Entry) -> Optional[float]:
        try:
            val = entry.get().strip()
            return float(val) if val else None
        except ValueError:
            return None

    def _get_date(self) -> date:
        if HAS_TKCALENDAR:
            d = self.date_picker.get_date()
            return d if isinstance(d, date) else date.today()
        else:
            d = self.date_entry.get().strip()
            return date.fromisoformat(d) if d else date.today()

    def _get_retorno_date(self) -> Optional[date]:
        if HAS_TKCALENDAR:
            d = self.retorno_picker.get_date()
            return d if isinstance(d, date) else None
        else:
            d = self.retorno_entry.get().strip()
            return date.fromisoformat(d) if d else None

    def _save(self):
        from ..models.consulta import Consulta
        
        consulta = Consulta(
            id=self.consulta.id if self.consulta else None,
            patient_id=self.patient.id,
            date=self._get_date(),
            queixa_principal=self.queixa_text.get("1.0", tk.END).strip(),
            observacoes=self.observacoes_text.get("1.0", tk.END).strip(),
            conduta=self.conduta_text.get("1.0", tk.END).strip(),
            proximo_retorno=self._get_retorno_date(),
            peso_registrado=self._get_float(self.peso_entry),
        )

        if self.on_save:
            self.on_save(consulta)
        self.destroy()
