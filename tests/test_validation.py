import pytest
from datetime import date, timedelta
from app.models.patient import Patient
from app.services.patient_service import PatientService
from app.repositories.patient_repository import PatientRepository

class DummyRepo(PatientRepository):
    def add(self, patient): return 1
    def update(self, patient): return True
    def delete(self, patient_id): return True
    def get_by_id(self, patient_id): return None
    def get_all(self): return []
    def search(self, query): return []

@pytest.fixture
def service():
    return PatientService(DummyRepo())

def test_valid_patient(service):
    p = Patient(name="João Silva", phone="(21) 99999-8888", birth_date=date(1990, 1, 1), email="joao@teste.com")
    res = service.validate(p)
    assert res.success

def test_missing_name(service):
    p = Patient(name="", phone="(21) 99999-8888", birth_date=date(1990, 1, 1))
    res = service.validate(p)
    assert not res.success
    assert any("nome completo é obrigatório" in e.message for e in res.errors)

def test_incomplete_name(service):
    p = Patient(name="João", phone="(21) 99999-8888", birth_date=date(1990, 1, 1))
    res = service.validate(p)
    assert not res.success
    assert any("nome completo" in e.message for e in res.errors)

def test_missing_phone(service):
    p = Patient(name="João Silva", phone="", birth_date=date(1990, 1, 1))
    res = service.validate(p)
    assert not res.success
    assert any("O telefone é obrigatório" in e.message for e in res.errors)

def test_invalid_phone_format(service):
    p = Patient(name="João Silva", phone="21999998888", birth_date=date(1990, 1, 1))
    res = service.validate(p)
    assert not res.success
    assert any("Telefone inválido" in e.message for e in res.errors)

def test_missing_birth_date(service):
    p = Patient(name="João Silva", phone="(21) 99999-8888", birth_date=None)
    res = service.validate(p)
    assert not res.success
    assert any("data de nascimento é obrigatória" in e.message for e in res.errors)

def test_future_birth_date(service):
    p = Patient(name="João Silva", phone="(21) 99999-8888", birth_date=date.today() + timedelta(days=1))
    res = service.validate(p)
    assert not res.success
    assert any("não pode ser futura" in e.message for e in res.errors)

def test_old_birth_date(service):
    p = Patient(name="João Silva", phone="(21) 99999-8888", birth_date=date(1899, 12, 31))
    res = service.validate(p)
    assert not res.success
    assert any("Data de nascimento inválida" in e.message for e in res.errors)

def test_invalid_email(service):
    p = Patient(name="João Silva", phone="(21) 99999-8888", birth_date=date(1990, 1, 1), email="email-invalido")
    res = service.validate(p)
    assert not res.success
    assert any("E-mail inválido" in e.message for e in res.errors)

def test_invalid_guardian_phone(service):
    p = Patient(name="João Silva", phone="(21) 99999-8888", birth_date=date(1990, 1, 1), guardian_phone="000")
    res = service.validate(p)
    assert not res.success
    assert any("Telefone do responsável inválido" in e.message for e in res.errors)
