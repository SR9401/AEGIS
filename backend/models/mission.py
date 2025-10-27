from .models import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, Index
from sqlalchemy import Enum as SQLEnum
import enum


class Status(enum.Enum):
    PLANNED = 'planned'
    ACTIVE = 'active'
    DONE = 'done'


class Mission(BaseModel):
    """classe qui definit une mission heriter de base model
        socle commun des classes.
    """
    __tablename__ = 'missions'

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(Status, name="mission_status", native_enum=True), default=Status.PLANNED, nullable=False)
    date = Column(DateTime(timezone=True), nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    created_by = Column(String(36), ForeignKey('users.id'), nullable=False)

    __table_args__ = (
        Index("ix_missions_status", "status"),
        Index("ix_missions_date", "date"),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'date': self.date.isoformat().replace("+00:00", "Z") if self.date else None,
            'lat': self.lat,
            'lon': self.lon,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat().replace("+00:00", "Z"),
            'updated_at': self.updated_at.isoformat().replace("+00:00", "Z"),
        }
