import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from db import Base

class BaseModel(Base):
    __abstract__ = True

 
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(datetime.UTC),
                        onupdate=lambda: datetime.now(datetime.UTC))
    def save(self):
        """Update the updated_at timestamp whenever the object is modified"""
        self.updated_at = datetime.now(datetime.UTC)

    def update(self, data):
        """Update the attributes of the object based on the provided dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        
    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat().replace("+00:00", "Z"),
            "updated_at": self.updated_at.isoformat().replace("+00:00", "Z")
        }
    