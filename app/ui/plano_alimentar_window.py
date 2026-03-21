import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.patient import Patient
    from ..models.plano_alimentar import PlanoAlimentar

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False


class PlanoAlimentarWindow(tk.Toplevel):
    def __init__(self, parent, patient: "Patient", plano: Optional["PlanoAlimentar"] = None, on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.patient = patient
        self.plano = plano
        self.on_save = on_save

        self.title("Plano Alimentar" if not plano else "Editar Plano")
        self.geometry("600x650")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        if plano:
            self._load_plano_data()

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
        ttk.Label(frame, text="Data:", font=("", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5)
        row += 1
        
        if HAS_TKCALENDAR:
            self.date_picker = DateEntry(frame, width=33, date_pattern="dd/mm/yyyy")
            self.date_picker.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        else:
            self.date_entry = ttk.Entry(frame, width=35)
            self.date_entry.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        refeicoes = [
            ("Café da Manhã:", "cafe_manha"),
            ("Lanche da Manhã:", "lanche_manha"),
            ("Almoço:", "almoco"),
            ("Lanche da Tarde:", "lanche_tarde"),
            ("Jantar:", "jantar"),
            ("Lanche da Noite:", "lanche_noite"),
        ]

        for label, attr in refeicoes:
            ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10,5))
            ttk.Label(frame, text=label, font=("", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky="w")
            row += 1
            text = tk.Text(frame, width=55, height=3)
            text.grid(row=row, column=0, columnspan=2, sticky="ew", pady=3)
            setattr(self, f"{attr}_text", text)
            row += 1

        ttk.Separator(frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(frame, text="MACRONUTRIENTES (opcional)", font=("", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1

        macros = [
            ("Calorias (kcal):", "calorias_entry"),
            ("Proteínas (g):", "proteinas_entry"),
            ("Carboidratos (g):", "carboidratos_entry"),
            ("Gorduras (g):", "gorduras_entry"),
        ]
        for i, (label, attr) in enumerate(macros):
            col = 0 if i % 2 == 0 else 1
            if i > 0 and i % 2 == 0:
                row += 1
            ttk.Label(frame, text=label).grid(row=row, column=col, sticky="w", pady=3)
            entry = ttk.Entry(frame, width=15)
            entry.grid(row=row, column=col+1, sticky="w", pady=3)
            setattr(self, attr, entry)
        row += 1

        ttk.Label(frame, text="Observações:").grid(row=row, column=0, sticky="nw", pady=5)
        row += 1
        self.observacoes_text = tk.Text(frame, width=55, height=3)
        self.observacoes_text.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        row += 1

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Salvar", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _load_plano_data(self):
        p = self.plano
        if HAS_TKCALENDAR:
            self.date_picker.set_date(p.date)
        else:
            self.date_entry.insert(0, p.date.isoformat())
        
        self.cafe_manha_text.insert("1.0", p.cafe_manha or "")
        self.lanche_manha_text.insert("1.0", p.lanche_manha or "")
        self.almoco_text.insert("1.0", p.almoco or "")
        self.lanche_tarde_text.insert("1.0", p.lanche_tarde or "")
        self.jantar_text.insert("1.0", p.jantar or "")
        self.lanche_noite_text.insert("1.0", p.lanche_noite or "")
        self.observacoes_text.insert("1.0", p.observacoes or "")
        
        if p.calorias:
            self.calorias_entry.insert(0, str(p.calorias))
        if p.proteinas:
            self.proteinas_entry.insert(0, str(p.proteinas))
        if p.carboidratos:
            self.carboidratos_entry.insert(0, str(p.carboidratos))
        if p.gorduras:
            self.gorduras_entry.insert(0, str(p.gorduras))

    def _get_float(self, entry: ttk.Entry) -> Optional[float]:
        try:
            val = entry.get().strip()
            return float(val) if val else None
        except ValueError:
            return None

    def _get_int(self, entry: ttk.Entry) -> Optional[int]:
        try:
            val = entry.get().strip()
            return int(val) if val else None
        except ValueError:
            return None

    def _save(self):
        from ..models.plano_alimentar import PlanoAlimentar
        
        plano = PlanoAlimentar(
            id=self.plano.id if self.plano else None,
            patient_id=self.patient.id,
            date=self._get_date(),
            cafe_manha=self.cafe_manha_text.get("1.0", tk.END).strip(),
            lanche_manha=self.lanche_manha_text.get("1.0", tk.END).strip(),
            almoco=self.almoco_text.get("1.0", tk.END).strip(),
            lanche_tarde=self.lanche_tarde_text.get("1.0", tk.END).strip(),
            jantar=self.jantar_text.get("1.0", tk.END).strip(),
            lanche_noite=self.lanche_noite_text.get("1.0", tk.END).strip(),
            observacoes=self.observacoes_text.get("1.0", tk.END).strip(),
            calorias=self._get_int(self.calorias_entry),
            proteinas=self._get_float(self.proteinas_entry),
            carboidratos=self._get_float(self.carboidratos_entry),
            gorduras=self._get_float(self.gorduras_entry),
        )

        if self.on_save:
            self.on_save(plano)
        self.destroy()

    def _get_date(self) -> date:
        if HAS_TKCALENDAR:
            d = self.date_picker.get_date()
            return d if isinstance(d, date) else date.today()
        else:
            d = self.date_entry.get().strip()
            return date.fromisoformat(d) if d else date.today()
