import os
import tempfile
from datetime import date

from app.controllers.anamnese_controller import AnamneseController
from app.controllers.patient_controller import PatientController
from app.models.anamnese import Anamnese
from app.models.patient import Patient
from app.repositories.sqlite_anamnese_repository import SQLiteAnamneseRepository
from app.repositories.sqlite_patient_repository import SQLitePatientRepository
from app.services.anamnese_service import AnamneseService
from app.services.patient_service import PatientService


def _build_controllers(db_path):
    patient_repository = SQLitePatientRepository(db_path)
    anamnese_repository = SQLiteAnamneseRepository(db_path)

    patient_controller = PatientController(PatientService(patient_repository))
    anamnese_controller = AnamneseController(AnamneseService(anamnese_repository))
    return patient_controller, anamnese_controller


def test_fluxo_completo_paciente_e_anamnese():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        patient_controller, anamnese_controller = _build_controllers(path)

        patient = Patient(
            name="Maria Silva",
            phone="(21) 99999-8888",
            birth_date=date(1990, 5, 10),
            status="Ativo",
        )
        created_patient = patient_controller.create_patient(patient)

        anamnese = Anamnese(
            patient_id=created_patient.id,
            data=date(2026, 3, 27),
            queixa_principal="Dificuldade para emagrecer",
            objetivo="Melhorar alimentacao",
            historico_saude="Sem doencas cronicas",
        )
        saved_anamnese = anamnese_controller.create_anamnese(anamnese)

        linked_anamnese = anamnese_controller.get_patient_anamnese(created_patient.id)

        assert created_patient.id is not None
        assert saved_anamnese.id is not None
        assert linked_anamnese is not None
        assert linked_anamnese.patient_id == created_patient.id
        assert linked_anamnese.queixa_principal == "Dificuldade para emagrecer"
        assert linked_anamnese.objetivo == "Melhorar alimentacao"
    finally:
        os.remove(path)


def test_fluxo_integrado_erro_sem_paciente_impede_persistencia():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        _, anamnese_controller = _build_controllers(path)

        anamnese = Anamnese(
            patient_id=None,
            data=date(2026, 3, 27),
            queixa_principal="Dificuldade para emagrecer",
        )

        try:
            anamnese_controller.create_anamnese(anamnese)
            assert False, "Era esperado ValueError"
        except ValueError as exc:
            assert "Paciente não identificado." in str(exc)

        assert anamnese_controller.get_patient_anamnese_history(0) == []
    finally:
        os.remove(path)


def test_fluxo_integrado_erro_sem_data_impede_persistencia():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        patient_controller, anamnese_controller = _build_controllers(path)
        patient = patient_controller.create_patient(
            Patient(
                name="Maria Silva",
                phone="(21) 99999-8888",
                birth_date=date(1990, 5, 10),
                status="Ativo",
            )
        )

        anamnese = Anamnese(
            patient_id=patient.id,
            data=None,
            queixa_principal="Dificuldade para emagrecer",
        )

        try:
            anamnese_controller.create_anamnese(anamnese)
            assert False, "Era esperado ValueError"
        except ValueError as exc:
            assert "A data da anamnese é obrigatória." in str(exc)

        assert anamnese_controller.get_patient_anamnese_history(patient.id) == []
    finally:
        os.remove(path)


def test_fluxo_integrado_erro_sem_queixa_principal_impede_persistencia():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        patient_controller, anamnese_controller = _build_controllers(path)
        patient = patient_controller.create_patient(
            Patient(
                name="Maria Silva",
                phone="(21) 99999-8888",
                birth_date=date(1990, 5, 10),
                status="Ativo",
            )
        )

        anamnese = Anamnese(
            patient_id=patient.id,
            data=date(2026, 3, 27),
            queixa_principal="",
        )

        try:
            anamnese_controller.create_anamnese(anamnese)
            assert False, "Era esperado ValueError"
        except ValueError as exc:
            assert "A queixa principal é obrigatória." in str(exc)

        assert anamnese_controller.get_patient_anamnese_history(patient.id) == []
    finally:
        os.remove(path)
