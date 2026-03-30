import os
import sqlite3
import tempfile
from datetime import date

import pytest

from app.models.anamnese import Anamnese
from app.models.patient import Patient
from app.repositories.sqlite_anamnese_repository import SQLiteAnamneseRepository
from app.repositories.sqlite_patient_repository import SQLitePatientRepository


@pytest.fixture
def repositories():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    patient_repository = SQLitePatientRepository(path)
    anamnese_repository = SQLiteAnamneseRepository(path)

    yield patient_repository, anamnese_repository

    if os.path.exists(path):
        os.remove(path)


def test_anamnese_com_patient_id_inexistente_falha_por_integridade(repositories):
    _, anamnese_repository = repositories

    with pytest.raises(sqlite3.IntegrityError):
        anamnese_repository.add(
            Anamnese(
                patient_id=9999,
                data=date(2026, 3, 27),
                queixa_principal="Dificuldade para emagrecer",
            )
        )


def test_excluir_paciente_remove_anamneses_relacionadas_por_cascade(repositories):
    patient_repository, anamnese_repository = repositories

    patient_id = patient_repository.add(
        Patient(
            name="Maria Silva",
            phone="(21) 99999-8888",
            birth_date=date(1990, 5, 10),
        )
    )

    anamnese_id = anamnese_repository.add(
        Anamnese(
            patient_id=patient_id,
            data=date(2026, 3, 27),
            queixa_principal="Dificuldade para emagrecer",
        )
    )

    assert anamnese_repository.get_by_id(anamnese_id) is not None

    deleted = patient_repository.delete(patient_id)

    assert deleted is True
    assert patient_repository.get_by_id(patient_id) is None
    assert anamnese_repository.get_by_id(anamnese_id) is None
    assert anamnese_repository.get_by_patient_history(patient_id) == []
