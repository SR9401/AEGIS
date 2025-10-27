# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base  # utilise le Base de ton projet (metadata)
import models  # s'assure que tous les modèles sont importés et enregistrés sur Base.metadata

@pytest.fixture(scope="session")
def engine():
    """
    Engine en mémoire pour les tests : rapide et isolé.
    """
    return create_engine("sqlite:///:memory:", echo=False)

@pytest.fixture(scope="session")
def tables(engine):
    """
    Crée toutes les tables une seule fois par session de test.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session(engine, tables):
    """
    Fournit une session transactionnelle par test.
    - Ouvre une connexion et démarre une transaction.
    - Rollback + close après le test pour isolation.
    """
    connection = engine.connect()
    trans = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        connection.close()
