import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from app.models.consulta import Consulta
from app.services.consulta_service import ConsultaService

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def consulta_service(mock_repository):
    return ConsultaService(mock_repository)

def test_defensive_consulta_loading():
    c = Consulta(
        patient_id="123",
        date="data_invalida",
        hora="texto_invalido",
        queixa_principal=None,
        proximo_retorno="retorno_sujo",
        peso_registrado="peso_zuado",
        id="texto_id",
        created_at="ts",
        updated_at=None
    )
    # Verifying defensive initialization via __post_init__
    assert c.patient_id == 123
    assert c.date == date.today()
    assert c.hora is None
    assert c.queixa_principal == ""
    assert c.proximo_retorno is None
    assert c.peso_registrado is None
    assert c.id is None
    assert c.created_at is None

def test_create_valid_consulta(consulta_service, mock_repository):
    c = Consulta(patient_id=1, date=date.today(), queixa_principal="Dor de cabeça")
    mock_repository.add.return_value = 10
    
    result = consulta_service.create(c)
    assert result.id == 10
    mock_repository.add.assert_called_once()

def test_create_consulta_without_queixa_fails(consulta_service):
    c = Consulta(patient_id=1, date=date.today(), queixa_principal="")
    with pytest.raises(ValueError) as e:
        consulta_service.create(c)
    assert "queixa principal" in str(e.value)

def test_create_consulta_negative_weight_fails(consulta_service):
    c = Consulta(patient_id=1, date=date.today(), queixa_principal="Ok", peso_registrado=-5.0)
    with pytest.raises(ValueError) as e:
        consulta_service.create(c)
    assert "peso" in str(e.value)

def test_retorno_before_date_fails(consulta_service):
    c = Consulta(
        patient_id=1, 
        date=date.today(), 
        queixa_principal="Ok", 
        proximo_retorno=date.today() - timedelta(days=1)
    )
    with pytest.raises(ValueError) as e:
        consulta_service.create(c)
    assert "retorno" in str(e.value)
