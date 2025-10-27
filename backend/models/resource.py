from .models import BaseModel
from sqlalchemy import Column, String, Text
from sqlalchemy import Enum as SQLEnum  # alias pour éviter la confusion
import enum


class ResourceStatus(str, enum.Enum):
    AVAILABLE = 'available'
    ASSIGNED = 'assigned'
    MAINTENANCE = 'maintenance'


class Resource(BaseModel):
    """classe qui définit les ressources (hérite de BaseModel)."""
    __tablename__ = 'resources'

    type = Column(String(50), nullable=False)
    label = Column(String(120), nullable=False, unique=True)


    status = Column(
        SQLEnum(ResourceStatus, name="resource_status", native_enum=False, validate_strings=True),
        default=ResourceStatus.AVAILABLE,
        nullable=False
    )

    details = Column(Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'label': self.label,
            'status': self.status.value,
            'details': self.details if self.details else None,
            'created_at': self.created_at.isoformat().replace("+00:00", "Z"),
            'updated_at': self.updated_at.isoformat().replace("+00:00", "Z"),
        }
