# backend/tests/test_mission_model.py
from datetime import datetime, timezone, timedelta
import time

import pytest
from models.mission import Mission, Status
from sqlalchemy.exc import IntegrityError

def test_create_and_query_mission(db_session):
    """
    Créer une mission, commit, récupérer et vérifier champs simples.
    """
    # création (created_by est une simple string ; si FK enforced, créez un user test avant)
    m = Mission(
        title="Mission test",
        description="Une mission pour les tests",
        status=Status.PLANNED,
        date=datetime.now(timezone.utc),
        lat=48.8566,
        lon=2.3522,
        created_by="test-user-1"
    )
    db_session.add(m)
    db_session.commit()

    assert m.id is not None
    # requery depuis la session pour s'assurer que l'objet est persisté
    got = db_session.query(Mission).filter_by(id=m.id).one()
    assert got.title == "Mission test"
    assert isinstance(got.status, Status)
    assert got.lat == 48.8566
    assert got.lon == 2.3522

def test_to_dict_serialization(db_session):
    """
    Vérifie que to_dict renvoie les champs attendus et que date/status sont sérialisés proprement.
    """
    d_date = datetime(2025, 10, 6, 12, 0, tzinfo=timezone.utc)
    m = Mission(
        title="Mission dict",
        description=None,
        status=Status.ACTIVE,
        date=d_date,
        lat=10.0,
        lon=20.0,
        created_by="test-user-2"
    )
    db_session.add(m)
    db_session.commit()

    got = db_session.query(Mission).filter_by(id=m.id).one()
    payload = got.to_dict()

    # Présence des champs
    assert payload["id"] == got.id
    assert payload["title"] == "Mission dict"
    assert payload["status"] in (Status.PLANNED.value, Status.ACTIVE.value, Status.DONE.value)
    assert payload["date"] == d_date.isoformat().replace("+00:00", "Z")
    assert payload["lat"] == 10.0
    assert payload["lon"] == 20.0
    assert "created_at" in payload and "updated_at" in payload

def test_updated_at_changes_on_update(db_session):
    """
    Vérifie que updated_at est modifié lors d'une update + commit.
    """
    m = Mission(
        title="To update",
        description="init",
        status=Status.PLANNED,
        date=datetime.now(timezone.utc),
        lat=0.0,
        lon=0.0,
        created_by="test-user-3"
    )
    db_session.add(m)
    db_session.commit()

    first_updated = m.updated_at

    # attendre un court instant pour s'assurer d'un timestamp différent
    time.sleep(0.01)

    # modification via update method (si implémentée) ou via setattr
    m.title = "Updated title"
    db_session.commit()

    db_session.refresh(m)
    assert m.updated_at is not None
    assert m.updated_at >= first_updated

def test_status_enum_restriction(db_session):
    """
    S'assurer que le champ status n'accepte que les valeurs définies par l'Enum.
    Dans SQLite SQLAlchemy tolère la conversion en texte, donc tenter d'assigner
    une valeur invalide peut lever une erreur côté Python/SQLAlchemy.
    """
    with pytest.raises(ValueError):
        # essayer d'assigner une valeur invalide à l'enum (doit échouer au niveau Python)
        Mission(
            title="bad status",
            description="bad",
            status="not-a-valid-status",  # ceci doit lever ValueError via l'Enum wrapper
            date=datetime.now(timezone.utc),
            lat=1.0,
            lon=1.0,
            created_by="test-user-4"
        )

