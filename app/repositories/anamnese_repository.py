from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from ..models.anamnese import Anamnese


class AnamneseRepository(ABC):
    @abstractmethod
    def add(self, anamnese: Anamnese) -> int: ...

    @abstractmethod
    def update(self, anamnese: Anamnese) -> bool: ...

    @abstractmethod
    def delete(self, anamnese_id: int) -> bool: ...

    @abstractmethod
    def get_by_id(self, anamnese_id: int) -> Optional[Anamnese]: ...

    @abstractmethod
    def get_by_patient(self, patient_id: int) -> Optional[Anamnese]: ...

    @abstractmethod
    def get_by_patient_history(self, patient_id: int) -> List[Anamnese]: ...
