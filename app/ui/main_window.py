import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import re
from typing import Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..controllers.patient_controller import PatientController
    from ..controllers.anamnese_controller import AnamneseController
    from ..controllers.consulta_controller import ConsultaController
    from ..controllers.avaliacao_controller import AvaliacaoController
    from ..controllers.plano_alimentar_controller import PlanoAlimentarController
    from ..models.patient import Patient

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

        self.title("Editar Paciente" if patient else "Novo Paciente")
        self.geometry("450x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_patient_data()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        row = 0

        ttk.Label(main_frame, text="Nome:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(main_frame, width=35)
        self.name_entry.grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(main_frame, text="Telefone:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(main_frame, width=35)
        self.phone_entry.grid(row=row, column=1, pady=5)
        self.phone_entry.bind("<KeyRelease>", self._on_phone_change)
        row += 1

        ttk.Label(main_frame, text="E-mail:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(main_frame, width=35)
        self.email_entry.grid(row=row, column=1, pady=5)
        row += 1

        ttk.Label(main_frame, text="Data de nascimento:").grid(row=row, column=0, sticky=tk.W, pady=5)
        if HAS_TKCALENDAR:
            self.birth_date_picker = DateEntry(main_frame, width=33, date_pattern="dd/mm/yyyy")
            self.birth_date_picker.grid(row=row, column=1, pady=5)
        else:
            self.birth_date_entry = ttk.Entry(main_frame, width=35)
            self.birth_date_entry.grid(row=row, column=1, pady=5)
            ttk.Label(main_frame, text="(AAAA-MM-DD)").grid(row=row, column=2, sticky=tk.W, padx=5)
            self.birth_date_entry.bind("<KeyRelease>", self._on_birth_change)
        row += 1

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Salvar", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _load_patient_data(self):
        if self.patient:
            self.phone_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.patient.name)
            self.phone_entry.insert(0, self.patient.phone)
            self.email_entry.insert(0, self.patient.email)

            if self.patient.birth_date:
                if HAS_TKCALENDAR:
                    self.birth_date_picker.set_date(self.patient.birth_date)
                else:
                    self.birth_date_entry.insert(0, self.patient.birth_date.isoformat())

    def _save(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        if HAS_TKCALENDAR:
            birth_date = self.birth_date_picker.get_date()
            if isinstance(birth_date, str):
                birth_date = date.fromisoformat(birth_date)
        else:
            birth_date_str = self.birth_date_entry.get().strip()
            birth_date = None
            if birth_date_str:
                try:
                    if "/" in birth_date_str:
                        day, month, year = birth_date_str.split("/")
                        birth_date = date(int(year), int(month), int(day))
                    else:
                        birth_date = date.fromisoformat(birth_date_str)
                except Exception:
                    messagebox.showerror("Erro", "Data de nascimento inválida. Use DD/MM/AAAA.")
                    return

        patient = self._create_patient(name, phone, email, birth_date)

        self.result = patient
        if self.on_save:
            self.on_save(patient)
        self.destroy()

    def _create_patient(self, name: str, phone: str, email: str, birth_date: Optional[date]):
        from ..models.patient import Patient
        return Patient(
            id=self.patient.id if self.patient else None,
            name=name,
            phone=phone,
            email=email,
            birth_date=birth_date,
        )

    def get_result(self) -> Optional["Patient"]:
        return self.result

    def _on_phone_change(self, _event=None):
        raw = re.sub(r"\D", "", self.phone_entry.get())[:11]

        if not raw:
            formatted = ""
        elif len(raw) <= 2:
            formatted = f"({raw}"
        elif len(raw) <= 7:
            formatted = f"({raw[:2]}){raw[2:]}"
        else:
            formatted = f"({raw[:2]}){raw[2:7]}-{raw[7:]}"

        self._set_entry(self.phone_entry, formatted)

    def _on_birth_change(self, _event=None):
        raw = re.sub(r"\D", "", self.birth_date_entry.get())
        if len(raw) > 8:
            raw = raw[:8]
        parts = []
        if len(raw) >= 2:
            parts.append(raw[:2])
        if len(raw) >= 4:
            parts.append(raw[2:4])
        if len(raw) > 4:
            parts.append(raw[4:])
        formatted = "/".join(parts)
        self._set_entry(self.birth_date_entry, formatted)

    def _set_entry(self, entry: ttk.Entry, text: str):
        current = entry.get()
        if current != text:
            pos = entry.index(tk.INSERT)
            entry.delete(0, tk.END)
            entry.insert(0, text)
            try:
                entry.icursor(pos)
            except tk.TclError:
                entry.icursor(tk.END)


class MainWindow:
    def __init__(
        self,
        patient_controller: "PatientController",
        anamnese_controller: "AnamneseController",
        consulta_controller: "ConsultaController",
        avaliacao_controller: "AvaliacaoController",
        plano_controller: "PlanoAlimentarController",
    ):
        self.patient_controller = patient_controller
        self.anamnese_controller = anamnese_controller
        self.consulta_controller = consulta_controller
        self.avaliacao_controller = avaliacao_controller
        self.plano_controller = plano_controller
        
        self.root = tk.Tk()
        self.root.title("Consultório Nutricionista")
        self.root.geometry("950x650")

        self._create_menu()
        self._create_widgets()
        self._load_patients()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        patient_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pacientes", menu=patient_menu)
        patient_menu.add_command(label="Novo Paciente", command=self._add_patient)
        patient_menu.add_separator()
        patient_menu.add_command(label="Sair", command=self.root.quit)

    def _create_widgets(self):
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(toolbar_frame, text="+ Novo", command=self._add_patient).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Editar", command=self._edit_patient).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Excluir", command=self._delete_patient).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar_frame, text="Prontuário", command=self._open_patient_detail).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="Anamnese", command=self._open_anamnese).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar_frame, text="Atualizar", command=self._load_patients).pack(side=tk.LEFT, padx=2)

        search_frame = ttk.Frame(toolbar_frame)
        search_frame.pack(side=tk.RIGHT)
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Buscar", command=self._search_patients).pack(side=tk.LEFT)
        self.search_entry.bind("<Return>", lambda e: self._search_patients())

        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "name", "phone", "email", "birth_date", "anamnese", "consultas")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Nome")
        self.tree.heading("phone", text="Telefone")
        self.tree.heading("email", text="E-mail")
        self.tree.heading("birth_date", text="Nasc.")
        self.tree.heading("anamnese", text="Anamnese")
        self.tree.heading("consultas", text="Consultas")

        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=200)
        self.tree.column("phone", width=110)
        self.tree.column("email", width=180)
        self.tree.column("birth_date", width=80, anchor=tk.CENTER)
        self.tree.column("anamnese", width=80, anchor=tk.CENTER)
        self.tree.column("consultas", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: self._open_patient_detail())

        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack(side=tk.LEFT)

    def _insert_patient_row(self, patient):
        birth_str = patient.birth_date.strftime("%d/%m/%Y") if patient.birth_date else ""
        has_anamnese = self.anamnese_controller.patient_has_anamnese(patient.id)
        num_consultas = len(self.consulta_controller.get_by_patient(patient.id))
        
        self.tree.insert("", tk.END, iid=patient.id, values=(
            patient.id,
            patient.name,
            patient.phone or "-",
            patient.email or "-",
            birth_str,
            "✅" if has_anamnese else "❌",
            num_consultas
        ))

    def _load_patients(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        patients = self.patient_controller.get_all_patients()
        for p in patients:
            self._insert_patient_row(p)

        self.status_label.config(text=f"Total de pacientes: {len(patients)}")

    def _search_patients(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_entry.get().strip()
        patients = self.patient_controller.search_patients(query)

        for p in patients:
            self._insert_patient_row(p)

        self.status_label.config(text=f"Encontrados: {len(patients)}")

    def _get_selected_patient_id(self) -> Optional[int]:
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um paciente na lista.")
            return None
        return int(selection[0])

    def _get_selected_patient(self):
        patient_id = self._get_selected_patient_id()
        if patient_id is None:
            return None
        return self.patient_controller.get_patient(patient_id)

    def _add_patient(self):
        def on_save(patient):
            try:
                self.patient_controller.create_patient(patient)
                self._load_patients()
                messagebox.showinfo("Sucesso", "Paciente cadastrado!")
                
                if messagebox.askyesno("Anamnese", "Deseja preencher a anamnese agora?"):
                    self.root.after(100, lambda: self._open_anamnese_for_patient(patient))
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        PatientFormWindow(self.root, on_save=on_save)

    def _edit_patient(self):
        patient = self._get_selected_patient()
        if patient is None:
            return

        def on_save(updated_patient):
            try:
                self.patient_controller.update_patient(updated_patient)
                self._load_patients()
                messagebox.showinfo("Sucesso", "Paciente atualizado!")
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        PatientFormWindow(self.root, patient=patient, on_save=on_save)

    def _delete_patient(self):
        patient_id = self._get_selected_patient_id()
        if patient_id is None:
            return

        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este paciente?"):
            try:
                self.patient_controller.delete_patient(patient_id)
                self._load_patients()
                messagebox.showinfo("Sucesso", "Paciente excluído!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _open_patient_detail(self):
        patient = self._get_selected_patient()
        if patient is None:
            return

        from .patient_detail_window import PatientDetailWindow
        PatientDetailWindow(
            self.root,
            patient=patient,
            patient_controller=self.patient_controller,
            anamnese_controller=self.anamnese_controller,
            consulta_controller=self.consulta_controller,
            avaliacao_controller=self.avaliacao_controller,
            plano_controller=self.plano_controller,
        )

    def _open_anamnese_for_patient(self, patient):
        def on_save(anamnese):
            try:
                self.anamnese_controller.create_anamnese(anamnese)
                self._load_patients()
                messagebox.showinfo("Sucesso", "Anamnese salva!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        from .anamnese_window import AnamneseWindow
        AnamneseWindow(self.root, patient=patient, on_save=on_save)

    def _open_anamnese(self):
        patient = self._get_selected_patient()
        if patient is None:
            return

        existing = self.anamnese_controller.get_patient_anamnese(patient.id)

        def on_save(anamnese):
            try:
                if existing:
                    self.anamnese_controller.update_anamnese(anamnese)
                else:
                    self.anamnese_controller.create_anamnese(anamnese)
                self._load_patients()
                messagebox.showinfo("Sucesso", "Anamnese salva!")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        from .anamnese_window import AnamneseWindow
        AnamneseWindow(self.root, patient=patient, anamnese=existing, on_save=on_save)

    def run(self):
        self.root.mainloop()
