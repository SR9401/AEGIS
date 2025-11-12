import os
import sys
import types
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("FLASK_ENV", "testing")

from backend.app import app
from backend.db import Base, engine, SessionLocal
from backend.models.user import User, Role
from backend.extensions import bcrypt

@pytest.fixture(scope="session", autouse=True)
def _create_schema_once():
    """Crée le schéma en mémoire pour toute la session PyTest."""
    with app.app_context():
        Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def db_session():
    """Session DB propre par test, avec rollback à la fin."""
    s = SessionLocal()
    try:
        yield s
    finally:
        s.rollback()
        s.close()

@pytest.fixture
def client():
    """Client Flask de test (HTTP)."""
    app.config["TESTING"] = True
    app.config.setdefault("JWT_SECRET_KEY", "test-secret")
    with app.test_client() as c:
        yield c

@pytest.fixture
def seed_admin(db_session):
    """Crée un utilisateur admin directement en base et le retourne."""
    pwd_hash = bcrypt.generate_password_hash("AdminFort123").decode("utf-8")
    u = User(
        first_name="Shakib",
        last_name="Admin",
        email="shakibadmin@local.fr",
        password_hash=pwd_hash,
        role=Role.ADMIN,
    )
    db_session.add(u)
    db_session.flush()
    return u

@pytest.fixture
def auth_headers(client, seed_admin):
    """Renvoie des headers Authorization valides (Bearer <token>) pour l’admin seedé."""
    resp = client.post(
        "/auth/login",
        json={"email": "shakibadmin@local.fr", "password": "AdminFort123"},
    )
    assert resp.status_code == 200, resp.get_json()
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
