from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.patient import Patient


class PatientRepository(ABC):
    @abstractmethod
    def add(self, patient: Patient) -> int: ...

    @abstractmethod
    def update(self, patient: Patient) -> bool: ...

    @abstractmethod
    def delete(self, patient_id: int) -> bool: ...

    @abstractmethod
    def get_by_id(self, patient_id: int) -> Optional[Patient]: ...

    @abstractmethod
    def get_all(self) -> List[Patient]: ...

    @abstractmethod
    def search(self, query: str) -> List[Patient]: ...
