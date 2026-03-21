import pytest
import tempfile
import os
from datetime import date
from pathlib import Path

from app.models.patient import Patient
from app.repositories.sqlite_patient_repository import SQLitePatientRepository


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    yield Path(db_path)
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def repository(temp_db):
    return SQLitePatientRepository(db_path=temp_db)


@pytest.fixture
def sample_patient():
    return Patient(
        name="Maria Santos",
        phone="(21)98765-4321",
        email="maria@email.com",
        birth_date=date(1985, 6, 20),
    )


class TestSQLitePatientRepository:
    def test_add_patient(self, repository, sample_patient):
        patient_id = repository.add(sample_patient)

        assert patient_id > 0
        saved_patient = repository.get_by_id(patient_id)
        assert saved_patient is not None
        assert saved_patient.name == sample_patient.name
        assert saved_patient.phone == sample_patient.phone
        assert saved_patient.email == sample_patient.email

    def test_add_and_get_patient(self, repository, sample_patient):
        patient_id = repository.add(sample_patient)

        result = repository.get_by_id(patient_id)

        assert result is not None
        assert result.id == patient_id
        assert result.name == "Maria Santos"

    def test_update_patient(self, repository, sample_patient):
        patient_id = repository.add(sample_patient)
        patient = repository.get_by_id(patient_id)
        patient.name = "Maria Silva"
        patient.phone = "(11)99999-1111"

        result = repository.update(patient)

        assert result is True
        updated = repository.get_by_id(patient_id)
        assert updated.name == "Maria Silva"
        assert updated.phone == "(11)99999-1111"

    def test_delete_patient(self, repository, sample_patient):
        patient_id = repository.add(sample_patient)

        result = repository.delete(patient_id)

        assert result is True
        assert repository.get_by_id(patient_id) is None

    def test_delete_nonexistent_patient(self, repository):
        result = repository.delete(9999)

        assert result is False

    def test_get_all_patients(self, repository):
        patients = [
            Patient(name="Ana", phone="(11)11111-1111", email="ana@x.com", birth_date=date(1990, 1, 1)),
            Patient(name="Beto", phone="(22)22222-2222", email="beto@x.com", birth_date=date(1991, 2, 2)),
            Patient(name="Carlos", phone="(33)33333-3333", email="carlos@x.com", birth_date=date(1992, 3, 3)),
        ]
        for p in patients:
            repository.add(p)

        result = repository.get_all()

        assert len(result) == 3
        names = [p.name for p in result]
        assert names == ["Ana", "Beto", "Carlos"]

    def test_search_patients_by_name(self, repository):
        patients = [
            Patient(name="João Silva", phone="(11)11111-1111", email="joao@x.com", birth_date=date(1990, 1, 1)),
            Patient(name="João Santos", phone="(22)22222-2222", email="jsantos@x.com", birth_date=date(1991, 2, 2)),
            Patient(name="Maria Silva", phone="(33)33333-3333", email="maria@x.com", birth_date=date(1992, 3, 3)),
        ]
        for p in patients:
            repository.add(p)

        result = repository.search("João")

        assert len(result) == 2

    def test_search_patients_by_email(self, repository):
        patients = [
            Patient(name="Ana", phone="(11)11111-1111", email="ana.work@company.com", birth_date=date(1990, 1, 1)),
            Patient(name="Beto", phone="(22)22222-2222", email="beto@other.com", birth_date=date(1991, 2, 2)),
        ]
        for p in patients:
            repository.add(p)

        result = repository.search("company")

        assert len(result) == 1
        assert result[0].name == "Ana"

    def test_search_patients_by_phone(self, repository):
        patients = [
            Patient(name="Ana", phone="(11)98765-4321", email="ana@x.com", birth_date=date(1990, 1, 1)),
            Patient(name="Beto", phone="(22)11111-1111", email="beto@x.com", birth_date=date(1991, 2, 2)),
        ]
        for p in patients:
            repository.add(p)

        result = repository.search("98765")

        assert len(result) == 1
        assert result[0].name == "Ana"

    def test_patient_timestamps_are_set(self, repository, sample_patient):
        patient_id = repository.add(sample_patient)

        patient = repository.get_by_id(patient_id)

        assert patient.created_at is not None
        assert patient.updated_at is not None
