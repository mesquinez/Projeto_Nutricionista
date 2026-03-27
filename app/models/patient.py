from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class Patient:
    name: str
    phone: str
    birth_date: Optional[date]
    id: Optional[int] = None
    social_name: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    uf: Optional[str] = None
    profession: Optional[str] = None
    observations: Optional[str] = None
    legal_guardian: Optional[str] = None
    guardian_phone: Optional[str] = None
    status: str = "Ativo"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        from ..utils.converters import coerce_string, coerce_date_or_none, coerce_int, coerce_datetime

        self.name = coerce_string(self.name)
        self.phone = coerce_string(self.phone)
        self.birth_date = coerce_date_or_none(self.birth_date)
        self.id = coerce_int(self.id)
        self.social_name = coerce_string(self.social_name)
        self.email = coerce_string(self.email)
        self.city = coerce_string(self.city)
        self.uf = coerce_string(self.uf)
        self.profession = coerce_string(self.profession)
        self.observations = coerce_string(self.observations)
        self.legal_guardian = coerce_string(self.legal_guardian)
        self.guardian_phone = coerce_string(self.guardian_phone)
        self.status = self.status if self.status else "Ativo"
        
        self.created_at = coerce_datetime(self.created_at)
        self.updated_at = coerce_datetime(self.updated_at)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'social_name': self.social_name,
            'phone': self.phone,
            'email': self.email,
            'birth_date': self.birth_date.isoformat() if isinstance(self.birth_date, date) else None,
            'city': self.city,
            'uf': self.uf,
            'profession': self.profession,
            'observations': self.observations,
            'legal_guardian': self.legal_guardian,
            'guardian_phone': self.guardian_phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else None,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else None,
        }
