import tkinter as tk
import re
from tkinter import ttk, messagebox
from datetime import date
from typing import Optional, Callable, TYPE_CHECKING

from app.ui.utils.formatters import format_phone, format_date_br

if TYPE_CHECKING:
    from app.models.patient import Patient

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False


class PatientFormWindow(tk.Toplevel):
    def __init__(self, parent, patient: Optional["Patient"] = None, on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.patient = patient
        self.on_save = on_save
        self.result = None

        self.title("Editar Paciente" if patient else "Cadastro de Paciente")
        self.geometry("600x700")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_patient_data()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Informações Principais
        sect_main = ttk.LabelFrame(main_frame, text=" Dados Principais ", padding="10")
        sect_main.pack(fill=tk.X, pady=(0, 10))

        # Grid para Dados Principais
        grid_main = ttk.Frame(sect_main)
        grid_main.pack(fill=tk.X)
        grid_main.columnconfigure(1, weight=1)

        # Nome Completo (*)
        ttk.Label(grid_main, text="Nome Completo *:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(grid_main)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        # Nome Social
        ttk.Label(grid_main, text="Nome Social:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.social_name_entry = ttk.Entry(grid_main)
        self.social_name_entry.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        # Segunda linha: Data Nasc e Telefone
        row2 = ttk.Frame(grid_main)
        row2.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=2)
        row2.columnconfigure(1, weight=1)
        row2.columnconfigure(3, weight=1)

        ttk.Label(row2, text="Data Nasc. *:").grid(row=0, column=0, sticky=tk.W)
        if HAS_TKCALENDAR:
            self.birth_date_picker = DateEntry(row2, width=12, date_pattern="dd/mm/yyyy", background="darkblue", foreground="white", borderwidth=2)
            self.birth_date_picker.grid(row=0, column=1, sticky=tk.W, padx=5)
        else:
            self.birth_date_entry = ttk.Entry(row2, width=15)
            self.birth_date_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
            self.birth_date_entry.bind("<KeyRelease>", self._on_birth_change)

        ttk.Label(row2, text="Telefone *:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.phone_entry = ttk.Entry(row2, width=18)
        self.phone_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.phone_entry.bind("<KeyRelease>", lambda e: self._on_phone_change(self.phone_entry))

        # E-mail
        ttk.Label(grid_main, text="E-mail:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.email_entry = ttk.Entry(grid_main)
        self.email_entry.grid(row=3, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        # Endereço e Profissão
        sect_extra = ttk.LabelFrame(main_frame, text=" Complemento ", padding="10")
        sect_extra.pack(fill=tk.X, pady=10)
        
        grid_extra = ttk.Frame(sect_extra)
        grid_extra.pack(fill=tk.X)
        grid_extra.columnconfigure(1, weight=1)

        # Cidade e UF
        row_loc = ttk.Frame(grid_extra)
        row_loc.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=2)
        row_loc.columnconfigure(1, weight=2)
        
        ttk.Label(row_loc, text="Cidade:").grid(row=0, column=0, sticky=tk.W)
        self.city_entry = ttk.Entry(row_loc)
        self.city_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        
        ttk.Label(row_loc, text="UF:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.uf_entry = ttk.Entry(row_loc, width=5)
        self.uf_entry.grid(row=0, column=3, sticky=tk.W, padx=5)

        # Profissão
        ttk.Label(grid_extra, text="Profissão:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.profession_entry = ttk.Entry(grid_extra)
        self.profession_entry.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        # Responsável (Menores/Acompanhantes)
        sect_resp = ttk.LabelFrame(main_frame, text=" Responsável Legal / Acompanhante ", padding="10")
        sect_resp.pack(fill=tk.X, pady=10)
        
        grid_resp = ttk.Frame(sect_resp)
        grid_resp.pack(fill=tk.X)
        grid_resp.columnconfigure(1, weight=1)

        ttk.Label(grid_resp, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.guardian_entry = ttk.Entry(grid_resp)
        self.guardian_entry.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=(5, 0))

        ttk.Label(grid_resp, text="Telefone:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.guardian_phone_entry = ttk.Entry(grid_resp)
        self.guardian_phone_entry.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        self.guardian_phone_entry.bind("<KeyRelease>", lambda e: self._on_phone_change(self.guardian_phone_entry))

        # Observações
        sect_obs = ttk.Frame(main_frame)
        sect_obs.pack(fill=tk.BOTH, expand=True)
        ttk.Label(sect_obs, text="Observações:").pack(anchor=tk.W)
        self.obs_text = tk.Text(sect_obs, height=4)
        self.obs_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Status (Apenas visível se for edição)
        self.status_var = tk.StringVar(value="Ativo")
        if self.patient:
            btn_status = ttk.Checkbutton(main_frame, text="Paciente Ativo", variable=self.status_var, 
                                        onvalue="Ativo", offvalue="Inativo")
            btn_status.pack(pady=5, anchor=tk.W)

        # Bottom Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Salvar Cadastro", command=self._save, style="Accent.TButton" if "Accent.TButton" in ttk.Style().theme_names() else "TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=5)

        self.name_entry.focus_set()

    def _load_patient_data(self):
        if self.patient:
            self.name_entry.insert(0, self.patient.name)
            self.social_name_entry.insert(0, self.patient.social_name or "")
            self.phone_entry.insert(0, self.patient.phone)
            self.email_entry.insert(0, self.patient.email or "")
            self.city_entry.insert(0, self.patient.city or "")
            self.uf_entry.insert(0, self.patient.uf or "")
            self.profession_entry.insert(0, self.patient.profession or "")
            self.guardian_entry.insert(0, self.patient.legal_guardian or "")
            self.guardian_phone_entry.insert(0, self.patient.guardian_phone or "")
            self.obs_text.insert("1.0", self.patient.observations or "")
            self.status_var.set(self.patient.status)

            if self.patient.birth_date:
                if HAS_TKCALENDAR:
                    self.birth_date_picker.set_date(self.patient.birth_date)
                else:
                    self.birth_date_entry.insert(0, self.patient.birth_date.strftime("%d/%m/%Y"))

    def _save(self):
        try:
            name = self.name_entry.get().strip()
            social_name = self.social_name_entry.get().strip()
            phone = self.phone_entry.get().strip()
            email = self.email_entry.get().strip()
            city = self.city_entry.get().strip()
            uf = self.uf_entry.get().upper().strip()
            profession = self.profession_entry.get().strip()
            legal_guardian = self.guardian_entry.get().strip()
            guardian_phone = self.guardian_phone_entry.get().strip()
            observations = self.obs_text.get("1.0", tk.END).strip()
            status = self.status_var.get()

            birth_date = None
            if HAS_TKCALENDAR:
                birth_date = self.birth_date_picker.get_date()
                if isinstance(birth_date, str):
                    birth_date = date.fromisoformat(birth_date)
            else:
                birth_date_str = self.birth_date_entry.get().strip()
                if birth_date_str:
                    try:
                        day, month, year = birth_date_str.split("/")
                        birth_date = date(int(year), int(month), int(day))
                    except Exception:
                        messagebox.showerror("Erro", "Data de nascimento inválida. Use DD/MM/AAAA.")
                        return

            patient = self._create_patient_obj(
                name=name, social_name=social_name, phone=phone, email=email,
                birth_date=birth_date, city=city, uf=uf, profession=profession,
                legal_guardian=legal_guardian, guardian_phone=guardian_phone,
                observations=observations, status=status
            )

            if self.on_save:
                success = self.on_save(patient)
                if success:
                    self.destroy()
        except Exception as e:
            messagebox.showerror("Erro de Cadastro", f"Ocorreu um erro ao salvar: {str(e)}")

    def _create_patient_obj(self, **kwargs):
        from app.models.patient import Patient
        return Patient(
            id=self.patient.id if self.patient else None,
            **kwargs
        )

    def _set_entry(self, entry: ttk.Entry, text: str):
        current = entry.get()
        if current != text:
            pos = entry.index(tk.INSERT)
            is_at_end = (pos == len(current))
            entry.delete(0, tk.END)
            entry.insert(0, text)
            if is_at_end:
                entry.icursor(tk.END)
            else:
                entry.icursor(pos)

    def _on_phone_change(self, entry, _event=None):
        raw_current = re.sub(r"\D", "", entry.get())
        formatted = format_phone(raw_current)
        self._set_entry(entry, formatted)

    def _on_birth_change(self, _event=None):
        formatted = format_date_br(self.birth_date_entry.get())
        self._set_entry(self.birth_date_entry, formatted)
