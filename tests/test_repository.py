import pytest
import sqlite3
from datetime import date
from app.repositories.sqlite_patient_repository import SQLitePatientRepository
from app.models.patient import Patient

import tempfile
import os

@pytest.fixture
def repo():
    # Usa arquivo temporário para manter o banco entre conexões da mesma instância
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    repo = SQLitePatientRepository(path)
    yield repo
    # Limpa
    os.remove(path)


def test_save_and_retrieve_patient(repo):
    p = Patient(
        name="Maria Aparecida",
        social_name="Mariazinha",
        phone="(11) 98888-7777",
        email="maria@teste.com",
        birth_date=date(1985, 5, 20),
        city="São Paulo",
        uf="SP",
        profession="Engenheira",
        observations="Paciente com dieta vegana",
        legal_guardian="",
        guardian_phone="",
        status="Ativo"
    )
    
    patient_id = repo.add(p)
    assert patient_id > 0
    
    saved = repo.get_by_id(patient_id)
    assert saved is not None
    assert saved.id == patient_id
    assert saved.name == "Maria Aparecida"
    assert saved.social_name == "Mariazinha"
    assert saved.phone == "(11) 98888-7777"
    assert saved.email == "maria@teste.com"
    assert saved.birth_date == date(1985, 5, 20)
    assert saved.city == "São Paulo"
    assert saved.uf == "SP"
    assert saved.profession == "Engenheira"
    assert saved.observations == "Paciente com dieta vegana"
    assert saved.status == "Ativo"

def test_all_new_fields_persisted(repo):
    p = Patient(
        name="João Menor",
        phone="(21) 97777-6666",
        birth_date=date(2010, 10, 10),
        legal_guardian="José Maior",
        guardian_phone="(21) 91111-2222"
    )
    patient_id = repo.add(p)
    
    saved = repo.get_by_id(patient_id)
    assert saved.legal_guardian == "José Maior"
    assert saved.guardian_phone == "(21) 91111-2222"

def test_update_patient(repo):
    p = Patient(
        name="Carlos Silva",
        phone="(21) 98888-1111",
        birth_date=date(1990, 1, 1),
    )
    patient_id = repo.add(p)
    
    p.id = patient_id
    p.city = "Rio de Janeiro"
    p.status = "Inativo"
    
    success = repo.update(p)
    assert success
    
    saved = repo.get_by_id(patient_id)
    assert saved.city == "Rio de Janeiro"
    assert saved.status == "Inativo"
