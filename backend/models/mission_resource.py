from .models import BaseModel
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UniqueConstraint
from datetime import datetime, timezone

class MissionResource(BaseModel):
    """pivot mission <-> resource (assignation)."""
    __tablename__ = 'mission_resources'

    mission_id  = Column(String(36), ForeignKey('missions.id', ondelete="CASCADE"),  nullable=False, index=True)
    resource_id = Column(String(36), ForeignKey('resources.id', ondelete="CASCADE"), nullable=False, index=True)

    assigned_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    note = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("mission_id", "resource_id", name="uq_mission_resource"),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'mission_id': self.mission_id,
            'resource_id': self.resource_id,
            'assigned_at': self.assigned_at.isoformat().replace("+00:00", "Z"),
            'note': self.note if self.note else None,
            'created_at': self.created_at.isoformat().replace("+00:00", "Z"),
            'updated_at': self.updated_at.isoformat().replace("+00:00", "Z"),
        }
