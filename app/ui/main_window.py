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
        ttk.Button(toolbar_frame, text="Nova Anamnese", command=self._open_anamnese).pack(side=tk.LEFT, padx=2)
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
                return True
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .patient_window import PatientFormWindow
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
                return True
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .patient_window import PatientFormWindow
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
        patients = self.patient_controller.get_all_patients()

        def on_save(anamnese):
            try:
                self.anamnese_controller.create_anamnese(anamnese)
                self._load_patients()
                messagebox.showinfo("Sucesso", "Anamnese salva!")
                return True
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .anamnese_window import AnamneseWindow
        AnamneseWindow(self.root, patient=patient, patients=patients, on_save=on_save)

    def _open_anamnese(self):
        patient = self._get_selected_patient()
        if patient is None:
            return

        patients = self.patient_controller.get_all_patients()

        def on_save(anamnese):
            try:
                self.anamnese_controller.create_anamnese(anamnese)
                self._load_patients()
                messagebox.showinfo("Sucesso", "Anamnese salva!")
                return True
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return False

        from .anamnese_window import AnamneseWindow
        AnamneseWindow(self.root, patient=patient, patients=patients, on_save=on_save)

    def run(self):
        self.root.mainloop()
