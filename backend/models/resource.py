from models import BaseModel
from sqlalchemy import Column, String, Enum, Text, DateTime, Float, ForeignKey
import enum


class ResourceStatus(enum.Enum):

    AVAILABLE = 'available'
    ASSIGNED = 'assigned'
    MAINTENANCE = 'maintenance'


class Resource(BaseModel):
    """classe qui definit les ressources heriter de base model
        socle commun des classes.
    """
    
    __tablename__ = 'resources'
    type = Column(String(50), nullable=False)
    label = Column(String(120), nullable=False, unique=True)
    status = Column(Enum(ResourceStatus), default=ResourceStatus.AVAILABLE, nullable=False)
    details = Column(Text, nullable=True)
     
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'label': self.label,
            'status': self.status.value,
            'details': self.details if self.details else None,
            'created_at': self.created_at.isoformat().replace("+00:00", "Z"),
            'updated_at': self.updated_at.isoformat().replace("+00:00", "Z")
        }
