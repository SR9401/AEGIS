from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

#URL de la base
# Pour le dev : SQLite (fichier local)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

#Engine (connexion à la DB)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

#Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base (tous tes modèles vont hériter de ça via BaseModel)
Base = declarative_base()
