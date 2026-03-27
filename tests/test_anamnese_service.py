from datetime import date
from unittest.mock import Mock

import pytest

from app.models.anamnese import Anamnese
from app.services.anamnese_service import AnamneseService


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def anamnese_service(mock_repository):
    return AnamneseService(mock_repository)


def test_salvar_anamnese_com_sucesso(anamnese_service, mock_repository):
    anamnese = Anamnese(
        patient_id=1,
        data=date(2026, 3, 27),
        queixa_principal="Dificuldade para emagrecer",
    )
    mock_repository.add.return_value = 10

    result = anamnese_service.create(anamnese)

    assert result.id == 10
    mock_repository.add.assert_called_once_with(anamnese)


def test_erro_sem_patient_id(anamnese_service):
    anamnese = Anamnese(
        patient_id=None,
        data=date(2026, 3, 27),
        queixa_principal="Dificuldade para emagrecer",
    )

    with pytest.raises(ValueError) as exc:
        anamnese_service.create(anamnese)

    assert "Paciente não identificado." in str(exc.value)


def test_erro_sem_data(anamnese_service):
    anamnese = Anamnese(
        patient_id=1,
        data=None,
        queixa_principal="Dificuldade para emagrecer",
    )

    with pytest.raises(ValueError) as exc:
        anamnese_service.create(anamnese)

    assert "A data da anamnese é obrigatória." in str(exc.value)


def test_erro_sem_queixa_principal(anamnese_service):
    anamnese = Anamnese(
        patient_id=1,
        data=date(2026, 3, 27),
        queixa_principal="",
    )

    with pytest.raises(ValueError) as exc:
        anamnese_service.create(anamnese)

    assert "A queixa principal é obrigatória." in str(exc.value)
