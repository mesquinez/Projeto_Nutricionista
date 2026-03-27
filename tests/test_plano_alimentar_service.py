import pytest
from datetime import date
from unittest.mock import Mock

from app.models.plano_alimentar import PlanoAlimentar
from app.services.plano_alimentar_service import PlanoAlimentarService

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def plano_service(mock_repository):
    return PlanoAlimentarService(mock_repository)

def test_defensive_plano_loading():
    p = PlanoAlimentar(
        patient_id="11",
        date="data_invalida",
        cafe_manha=None,
        calorias="texto_zoado",
        proteinas="120,5", # virgula local
        id="zoado",
        created_at="ts",
        updated_at=None
    )
    
    assert p.patient_id == 11
    assert isinstance(p.date, date)
    assert p.cafe_manha == ""
    assert p.calorias is None
    assert p.proteinas == 120.5
    assert p.id is None
    assert p.created_at is None

def test_plano_calcula_calorias():
    p = PlanoAlimentar(patient_id=1, date=date.today(), proteinas=100.0, carboidratos=150.0, gorduras=30.0)
    # (100*4) + (150*4) + (30*9) = 400 + 600 + 270 = 1270
    assert p.calcular_calorias_totais() == 1270

def test_create_valid_plano(plano_service, mock_repository):
    p = PlanoAlimentar(patient_id=1, date=date.today(), calorias=2000)
    mock_repository.add.return_value = 10
    
    result = plano_service.create(p)
    assert result.id == 10
    mock_repository.add.assert_called_once()

def test_create_plano_negative_macros_fails(plano_service):
    p = PlanoAlimentar(patient_id=1, date=date.today(), gorduras=-5.0)
    with pytest.raises(ValueError) as e:
        plano_service.create(p)
    assert "negativas" in str(e.value)
