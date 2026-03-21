from pathlib import Path

from app.config import settings, logger
from app.repositories import (
    SQLitePatientRepository, SQLiteAnamneseRepository,
    SQLiteConsultaRepository, SQLiteAvaliacaoRepository,
    SQLitePlanoAlimentarRepository
)
from app.services import (
    PatientService, AnamneseService,
    ConsultaService, AvaliacaoService,
    PlanoAlimentarService
)
from app.controllers import (
    PatientController, AnamneseController,
    ConsultaController, AvaliacaoController,
    PlanoAlimentarController
)
from app.ui.main_window import MainWindow


def create_app() -> MainWindow:
    logger.info("Iniciando aplicação...")

    patient_repo = SQLitePatientRepository(db_path=settings.db_path)
    patient_repo._init_db()
    patient_service = PatientService(repository=patient_repo)
    patient_controller = PatientController(service=patient_service)

    anamnese_repo = SQLiteAnamneseRepository(db_path=settings.db_path)
    anamnese_repo._init_db()
    anamnese_service = AnamneseService(repository=anamnese_repo)
    anamnese_controller = AnamneseController(service=anamnese_service)

    consulta_repo = SQLiteConsultaRepository(db_path=settings.db_path)
    consulta_repo._init_db()
    consulta_service = ConsultaService(repository=consulta_repo)
    consulta_controller = ConsultaController(service=consulta_service)

    avaliacao_repo = SQLiteAvaliacaoRepository(db_path=settings.db_path)
    avaliacao_repo._init_db()
    avaliacao_service = AvaliacaoService(repository=avaliacao_repo)
    avaliacao_controller = AvaliacaoController(service=avaliacao_service)

    plano_repo = SQLitePlanoAlimentarRepository(db_path=settings.db_path)
    plano_repo._init_db()
    plano_service = PlanoAlimentarService(repository=plano_repo)
    plano_controller = PlanoAlimentarController(service=plano_service)

    app = MainWindow(
        patient_controller=patient_controller,
        anamnese_controller=anamnese_controller,
        consulta_controller=consulta_controller,
        avaliacao_controller=avaliacao_controller,
        plano_controller=plano_controller,
    )

    logger.info("Aplicação iniciada com sucesso")
    return app


def run_app() -> None:
    app = create_app()
    app.run()


if __name__ == "__main__":
    run_app()
