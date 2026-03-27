import pytest
from datetime import date
from unittest.mock import Mock

from app.models.anamnese import Anamnese
from app.services.anamnese_service import AnamneseService

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def anamnese_service(mock_repository):
    return AnamneseService(mock_repository)

def test_defensive_anamnese_loading():
    a = Anamnese(
        patient_id="11",
        date="data_invalida",
        objetivo_principal=None,
        peso_maximo="120,5", # virgula local
        peso_minimo="texto_zoado",
        refeicoes_dia="3",
        habitos_alimentares=None,
        id="zoado",
        created_at="ts",
        updated_at=None
    )
    
    assert a.patient_id == 11
    assert isinstance(a.date, date)
    assert a.objetivo_principal == ""
    assert a.peso_maximo == 120.5
    assert a.peso_minimo is None
    assert a.refeicoes_dia == 3
    assert a.habitos_alimentares == ""
    assert a.id is None
    assert a.created_at is None

def test_create_valid_anamnese(anamnese_service, mock_repository):
    a = Anamnese(patient_id=1, date=date.today(), objetivo_principal="Emagrecer", peso_maximo=100.0)
    mock_repository.add.return_value = 10
    
    result = anamnese_service.create(a)
    assert result.id == 10
    mock_repository.add.assert_called_once()

def test_create_anamnese_sem_objetivo_fails(anamnese_service):
    a = Anamnese(patient_id=1, date=date.today(), objetivo_principal="")
    with pytest.raises(ValueError) as e:
        anamnese_service.create(a)
    assert "objetivo" in str(e.value)

def test_create_anamnese_negative_weight_fails(anamnese_service):
    a = Anamnese(patient_id=1, date=date.today(), objetivo_principal="A", peso_maximo=-5.0)
    with pytest.raises(ValueError) as e:
        anamnese_service.create(a)
    assert "Peso máximo não pode ser negativo" in str(e.value)

def test_create_anamnese_min_maior_que_max_fails(anamnese_service):
    a = Anamnese(patient_id=1, date=date.today(), objetivo_principal="A", peso_minimo=80.0, peso_maximo=70.0)
    with pytest.raises(ValueError) as e:
        anamnese_service.create(a)
    assert "mínimo informado é maior" in str(e.value)
