"""
Script de test minimal pour valider les modèles ORM :
- User (unicité email)
- Mission (FK created_by, dates ISO)
- Resource (unicité label)
- MissionResource (unicité composée mission_id + resource_id)

Exécution :
    cd backend
    python test_db.py
"""

from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

# === Imports projet ===
# Assure-toi que db.py et models/__init__.py exposent bien Base, engine, SessionLocal et les classes
from db import Base, engine, SessionLocal
from models import User, Mission, Resource, MissionResource, Role, Status, ResourceStatus

# --- helpers ---------------------------------------------------------------

def now_utc():
    return datetime.now(timezone.utc)

def p(title, data):
    print(f"\n=== {title} ===")
    print(data)

# --- scénario de test ------------------------------------------------------

def main():
    # 0) (MVP) créer les tables si besoin
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # 1) User : création + unicité email
        u1 = User(
            first_name="Shakib",
            last_name="Rojas",
            email="shakib@example.com",
            password_hash="hashed:demo",  # placeholder (tu mettras bcrypt plus tard)
            role=Role.OBSERVER,
        )
        session.add(u1)
        session.commit()
        p("User créé", u1.to_dict())

        # tentative de doublon email
        u2 = User(
            first_name="Alice",
            last_name="Doe",
            email="shakib@example.com",  # même email -> doit échouer
            password_hash="hashed:demo2",
            role=Role.COORDINATOR,
        )
        session.add(u2)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            p("Contrainte OK", "Email déjà utilisé : IntegrityError interceptée")

        # 2) Resource : création + unicité label
        r1 = Resource(
            type="vehicle",
            label="Truck-001",
            status=ResourceStatus.AVAILABLE,
            details="Camion logistique 5t",
        )
        session.add(r1)
        session.commit()
        p("Resource créée", r1.to_dict())

        # 3) Mission : création (date nullable / coord obligatoires / FK created_by)
        m1 = Mission(
            title="Patrouille Nord",
            description="Surveillance de zone",
            status=Status.PLANNED,
            date=now_utc(),  # ou None si tu veux tester le guard
            lat=44.8378,
            lon=-0.5792,
            created_by=u1.id,  # FK vers users.id
        )
        session.add(m1)
        session.commit()
        p("Mission créée", m1.to_dict())

        # 4) MissionResource : affectation + unicité composée
        mr1 = MissionResource(
            mission_id=m1.id,
            resource_id=r1.id,
            assigned_at=now_utc(),
            note="Départ 08:00Z",
        )
        session.add(mr1)
        session.commit()
        p("Affectation mission<->resource", mr1.to_dict())

        # tentative de doublon (même paire mission_id + resource_id)
        mr2 = MissionResource(
            mission_id=m1.id,
            resource_id=r1.id,
            assigned_at=now_utc(),
            note="Doublon volontaire",
        )
        session.add(mr2)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            p("Contrainte OK", "Doublon mission/resource bloqué (UniqueConstraint)")

        # 5) Petites vérifications de lecture
        users = session.query(User).all()
        missions = session.query(Mission).all()
        resources = session.query(Resource).all()

        p("Users en base", [u.to_dict() for u in users])
        p("Missions en base", [m.to_dict() for m in missions])
        p("Resources en base", [r.to_dict() for r in resources])

    finally:
        session.close()


if __name__ == "__main__":
    main()
