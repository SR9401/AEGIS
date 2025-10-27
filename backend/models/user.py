from .models import BaseModel
from sqlalchemy import Column, String
from sqlalchemy import Enum as SQLEnum
import enum


class Role(enum.Enum):
    ADMIN = 'admin'
    COORDINATOR = 'coordinator'
    OBSERVER = 'observer'


class User(BaseModel):
    """classe qui definit un utilisateur heriter de base model
        socle commun des classes.
    """
    __tablename__ = 'users'

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    role = Column(SQLEnum(Role, name="user_role", native_enum=True), default=Role.OBSERVER, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat().replace("+00:00", "Z"),
            'updated_at': self.updated_at.isoformat().replace("+00:00", "Z"),
        }
