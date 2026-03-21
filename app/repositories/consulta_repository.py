from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from ..models.consulta import Consulta


class ConsultaRepository(ABC):
    @abstractmethod
    def add(self, consulta: Consulta) -> int: ...
    @abstractmethod
    def update(self, consulta: Consulta) -> bool: ...
    @abstractmethod
    def delete(self, consulta_id: int) -> bool: ...
    @abstractmethod
    def get_by_id(self, consulta_id: int) -> Optional[Consulta]: ...
    @abstractmethod
    def get_by_patient(self, patient_id: int) -> List[Consulta]: ...
    @abstractmethod
    def get_last_by_patient(self, patient_id: int) -> Optional[Consulta]: ...
