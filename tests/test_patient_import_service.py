import os
import tempfile
from pathlib import Path

import pytest

from app.repositories.sqlite_patient_repository import SQLitePatientRepository
from app.services.patient_service import PatientService


@pytest.fixture
def patient_service():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    repository = SQLitePatientRepository(path)
    service = PatientService(repository)

    yield service

    if os.path.exists(path):
        os.remove(path)


def _write_csv(rows, header=None):
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    csv_path = Path(path)

    lines = [",".join(header or ["nome_completo", "data_nascimento", "telefone"])]
    lines.extend(rows)
    csv_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path


def test_importacao_com_sucesso(patient_service):
    csv_path = _write_csv(
        [
            "Maria Silva,10/05/1990,(21)99999-8888",
            "Joao Costa,22/08/1985,(21)98888-7777",
        ]
    )

    try:
        result = patient_service.import_from_csv(csv_path)

        assert result.success_count == 2
        assert result.failure_count == 0
        assert len(result.errors) == 0
        assert len(patient_service.get_all()) == 2
    finally:
        csv_path.unlink(missing_ok=True)


def test_linha_sem_nome(patient_service):
    csv_path = _write_csv(
        [
            ",10/05/1990,(21)99999-8888",
        ]
    )

    try:
        result = patient_service.import_from_csv(csv_path)

        assert result.success_count == 0
        assert result.failure_count == 1
        assert "nome completo" in result.errors[0].reason.lower()
    finally:
        csv_path.unlink(missing_ok=True)


def test_linha_sem_telefone(patient_service):
    csv_path = _write_csv(
        [
            "Maria Silva,10/05/1990,",
        ]
    )

    try:
        result = patient_service.import_from_csv(csv_path)

        assert result.success_count == 0
        assert result.failure_count == 1
        assert "telefone" in result.errors[0].reason.lower()
    finally:
        csv_path.unlink(missing_ok=True)


def test_linha_sem_data(patient_service):
    csv_path = _write_csv(
        [
            "Maria Silva,,(21)99999-8888",
        ]
    )

    try:
        result = patient_service.import_from_csv(csv_path)

        assert result.success_count == 0
        assert result.failure_count == 1
        assert "data de nascimento" in result.errors[0].reason.lower()
    finally:
        csv_path.unlink(missing_ok=True)


def test_telefone_invalido(patient_service):
    csv_path = _write_csv(
        [
            "Maria Silva,10/05/1990,21999998888",
        ]
    )

    try:
        result = patient_service.import_from_csv(csv_path)

        assert result.success_count == 0
        assert result.failure_count == 1
        assert "telefone inv" in result.errors[0].reason.lower()
    finally:
        csv_path.unlink(missing_ok=True)


def test_data_invalida(patient_service):
    csv_path = _write_csv(
        [
            "Maria Silva,31/02/1990,(21)99999-8888",
        ]
    )

    try:
        result = patient_service.import_from_csv(csv_path)

        assert result.success_count == 0
        assert result.failure_count == 1
        assert "data de nascimento" in result.errors[0].reason.lower()
    finally:
        csv_path.unlink(missing_ok=True)


def test_mistura_linhas_validas_e_invalidas(patient_service):
    csv_path = _write_csv(
        [
            "Maria Silva,10/05/1990,(21)99999-8888",
            "Joao,22/08/1985,(21)98888-7777",
            "Ana Costa,01/01/1992,(21)97777-6666",
            "Carlos Lima,,(21)96666-5555",
        ]
    )

    try:
        result = patient_service.import_from_csv(csv_path)

        assert result.success_count == 2
        assert result.failure_count == 2
        assert len(patient_service.get_all()) == 2
        reasons = " ".join(error.reason.lower() for error in result.errors)
        assert "nome completo" in reasons
        assert "data de nascimento" in reasons
    finally:
        csv_path.unlink(missing_ok=True)


def test_resumo_final_da_importacao(patient_service):
    csv_path = _write_csv(
        [
            "Maria Silva,10/05/1990,(21)99999-8888",
            "Linha Sem Telefone,10/05/1990,",
            "Linha Sem Data,,(21)98888-7777",
        ]
    )

    try:
        result = patient_service.import_from_csv(csv_path)

        assert result.total_processed == 3
        assert result.success_count == 1
        assert result.failure_count == 2
        assert result.errors[0].line_number == 3
        assert result.errors[1].line_number == 4
    finally:
        csv_path.unlink(missing_ok=True)


def test_colunas_equivalentes_e_colunas_extras_sao_aceitas(patient_service):
    csv_path = _write_csv(
        [
            "Maria Silva,1990-05-10,(21)99999-8888,ignorar",
            "Joao Costa,1985-08-22,(21)98888-7777,ignorar tambem",
        ],
        header=["nome", "birth_date", "phone", "observacoes"],
    )

    try:
        result = patient_service.import_from_csv(csv_path)

        assert result.success_count == 2
        assert result.failure_count == 0
        patients = patient_service.get_all()
        assert len(patients) == 2
        assert patients[0].observations == ""
        assert patients[1].observations == ""
    finally:
        csv_path.unlink(missing_ok=True)
