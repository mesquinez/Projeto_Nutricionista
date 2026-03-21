from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from ..models.plano_alimentar import PlanoAlimentar


class PlanoAlimentarRepository(ABC):
    @abstractmethod
    def add(self, plano: PlanoAlimentar) -> int: ...
    @abstractmethod
    def update(self, plano: PlanoAlimentar) -> bool: ...
    @abstractmethod
    def delete(self, plano_id: int) -> bool: ...
    @abstractmethod
    def get_by_id(self, plano_id: int) -> Optional[PlanoAlimentar]: ...
    @abstractmethod
    def get_by_patient(self, patient_id: int) -> List[PlanoAlimentar]: ...
    @abstractmethod
    def get_last_by_patient(self, patient_id: int) -> Optional[PlanoAlimentar]: ...
