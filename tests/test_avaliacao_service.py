import pytest
from datetime import date
from unittest.mock import Mock

from app.models.avaliacao import Avaliacao
from app.services.avaliacao_service import AvaliacaoService

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def avaliacao_service(mock_repository):
    return AvaliacaoService(mock_repository)

def test_defensive_avaliacao_loading():
    a = Avaliacao(
        patient_id="99",
        date="data_invalida",
        peso="85,6", # virgula local
        altura=" 180.5   ",
        pressao_sistolica="120",
        observacoes=None,
        id="zoado",
        created_at="ts",
        updated_at=None
    )
    
    assert a.patient_id == 99
    assert isinstance(a.date, date)
    assert a.peso == 85.6
    assert a.altura == 180.5
    assert a.pressao_sistolica == 120
    assert a.observacoes == ""
    assert a.id is None
    assert a.created_at is None

def test_avaliacao_calcula_imc():
    a = Avaliacao(patient_id=1, date=date.today(), peso=100.0, altura=200.0)
    assert a.calcular_imc() == 25.0

def test_create_valid_avaliacao(avaliacao_service, mock_repository):
    a = Avaliacao(patient_id=1, date=date.today(), peso=80, altura=180)
    mock_repository.add.return_value = 10
    
    result = avaliacao_service.create(a)
    assert result.id == 10
    mock_repository.add.assert_called_once()

def test_create_avaliacao_negative_peso_fails(avaliacao_service):
    a = Avaliacao(patient_id=1, date=date.today(), peso=-5.0)
    with pytest.raises(ValueError) as e:
        avaliacao_service.create(a)
    assert "peso deve ser maior" in str(e.value)

def test_create_avaliacao_negative_altura_fails(avaliacao_service):
    a = Avaliacao(patient_id=1, date=date.today(), altura=-1.0)
    with pytest.raises(ValueError) as e:
        avaliacao_service.create(a)
    assert "altura deve ser maior" in str(e.value)
