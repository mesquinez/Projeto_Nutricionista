import logging
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    db_path: Path = Path("nutritionist.db")
    app_title: str = "Consultório Nutricionista - Pacientes"
    log_level: str = "INFO"
    log_file: Path = Path("app.log")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=Path(os.getenv("DB_PATH", "nutritionist.db")),
            app_title=os.getenv("APP_TITLE", "Consultório Nutricionista - Pacientes"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=Path(os.getenv("LOG_FILE", "app.log")),
        )


def setup_logging(settings: Settings) -> logging.Logger:
    logger = logging.getLogger("nutricionista")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if not logger.handlers:
        file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


settings = Settings.from_env()
logger = setup_logging(settings)
