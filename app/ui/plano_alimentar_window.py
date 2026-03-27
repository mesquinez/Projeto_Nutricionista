import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.patient import Patient
    from ..models.plano_alimentar import PlanoAlimentar

from app.ui.utils.formatters import format_date_br

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
            ttk.Label(frame, text="(DD/MM/AAAA)").grid(row=row, column=2, sticky="w", padx=5)
            self.date_entry.bind("<KeyRelease>", self._on_date_change)
            self.date_entry.bind("<Return>", lambda e: self.cafe_manha_text.focus_set())
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
            entry.bind("<Return>", lambda e: self._save())
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

        if HAS_TKCALENDAR:
            self.date_picker.focus_set()
        else:
            self.date_entry.focus_set()

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
        
        if p.calorias is not None:
            self.calorias_entry.insert(0, str(p.calorias))
        if p.proteinas is not None:
            self.proteinas_entry.insert(0, str(p.proteinas))
        if p.carboidratos is not None:
            self.carboidratos_entry.insert(0, str(p.carboidratos))
        if p.gorduras is not None:
            self.gorduras_entry.insert(0, str(p.gorduras))

    def _on_date_change(self, event=None):
        if not HAS_TKCALENDAR:
            formatted = format_date_br(self.date_entry.get())
            current_pos = self.date_entry.index(tk.INSERT)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, formatted)
            self.date_entry.icursor(current_pos)



    def _save(self):
        from ..models.plano_alimentar import PlanoAlimentar
        from ..utils.validators import is_valid_number, is_valid_int
        from ..utils.converters import coerce_date_or_none
        
        errors = []
        if not is_valid_int(self.calorias_entry.get().strip()):
            errors.append("Calorias (kcal) deve ser um número inteiro.")
        if not is_valid_number(self.proteinas_entry.get().strip()):
            errors.append("Proteínas (g) deve ser um número.")
        if not is_valid_number(self.carboidratos_entry.get().strip()):
            errors.append("Carboidratos (g) deve ser um número.")
        if not is_valid_number(self.gorduras_entry.get().strip()):
            errors.append("Gorduras (g) deve ser um número.")
            
        if not HAS_TKCALENDAR:
            d_txt = self.date_entry.get().strip()
            if d_txt and not coerce_date_or_none(d_txt):
                errors.append("Formato de data inválido (use AAAA-MM-DD).")

        if errors:
            messagebox.showerror("Erro de Preenchimento", "\n".join(errors))
            return

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
            calorias=self.calorias_entry.get().strip() or None,
            proteinas=self.proteinas_entry.get().strip() or None,
            carboidratos=self.carboidratos_entry.get().strip() or None,
            gorduras=self.gorduras_entry.get().strip() or None,
        )

        if self.on_save:
            success = self.on_save(plano)
            if not success:
               return # abort window murder
        self.destroy()

    def _get_date(self) -> date:
        from ..utils.converters import coerce_date_or_today
        if HAS_TKCALENDAR:
            d = self.date_picker.get_date()
            return d if isinstance(d, date) else date.today()
        else:
            d = self.date_entry.get().strip()
            # Suporte a DD/MM/AAAA
            from ..utils.converters import coerce_date_or_today
            if "/" in d:
                try:
                    parts = d.split("/")
                    d = f"{parts[2]}-{parts[1]}-{parts[0]}"
                except: pass
            return coerce_date_or_today(d)
