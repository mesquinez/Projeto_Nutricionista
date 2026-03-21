from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from ..models.avaliacao import Avaliacao


class AvaliacaoRepository(ABC):
    @abstractmethod
    def add(self, avaliacao: Avaliacao) -> int: ...
    @abstractmethod
    def update(self, avaliacao: Avaliacao) -> bool: ...
    @abstractmethod
    def delete(self, avaliacao_id: int) -> bool: ...
    @abstractmethod
    def get_by_id(self, avaliacao_id: int) -> Optional[Avaliacao]: ...
    @abstractmethod
    def get_by_patient(self, patient_id: int) -> List[Avaliacao]: ...
    @abstractmethod
    def get_last_by_patient(self, patient_id: int) -> Optional[Avaliacao]: ...
