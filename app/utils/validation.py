from dataclasses import dataclass
from typing import List

@dataclass
class ValidationError:
    field: str
    message: str

@dataclass
class ValidationResult:
    success: bool
    errors: List[ValidationError]

    @property
    def error_messages(self) -> List[str]:
        return [e.message for e in self.errors]
