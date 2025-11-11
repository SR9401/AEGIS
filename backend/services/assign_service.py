# backend/services/assign_service.py
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError
from models.mission_resource import MissionResource
from models.mission import Mission
from models.resource import Resource, ResourceStatus
from sqlalchemy import exists, select
from datetime import datetime, timezone

class AssignService:
    @staticmethod
    def create_assignment(session, mission_id: str, resource_id: str, note: str | None = None) -> MissionResource:
        # Vérifs d'existence
        m = session.get(Mission, mission_id)
        if not m:
            raise ValueError("not_found_mission")

        r = session.get(Resource, resource_id)
        if not r:
            raise ValueError("not_found_resource")

        link = MissionResource(mission_id=mission_id, resource_id=resource_id, note=note or None)
        try:
            session.add(link)

            # Optionnel: passer la ressource en 'assigned'
            if r.status != ResourceStatus.ASSIGNED:
                r.status = ResourceStatus.ASSIGNED
                session.add(r)

            session.flush()
        except IntegrityError:
            session.rollback()
            # contrainte unique mission_id+resource_id
            raise ValueError("duplicate_assignment")

        return link

    @staticmethod
    def delete_assignment(session, assign_id: str) -> None:
        link = session.get(MissionResource, assign_id)
        if not link:
            raise ValueError("not_found_assign")

        # Optionnel: remettre la ressource en available s'il n'y a plus d'assignations
        res = session.get(Resource, link.resource_id)

        session.delete(link)
        session.flush()

        if res:
            remaining = session.query(MissionResource).filter_by(resource_id=res.id).count()
            if remaining == 0 and res.status == ResourceStatus.ASSIGNED:
                res.status = ResourceStatus.AVAILABLE
                session.add(res)
                session.flush()
def refresh_resource_status(session, resource_id: str):
    """ASSIGNED si au moins un lien mission_resource existe, sinon AVAILABLE (sauf si MAINTENANCE)."""
    res = session.get(Resource, resource_id)
    if not res:
        return

    # Si la ressource est en maintenance, on ne la force pas en AVAILABLE
    if res.status == ResourceStatus.MAINTENANCE:
        return

    has_links = session.execute(
        select(exists().where(MissionResource.resource_id == resource_id))
    ).scalar()

    res.status = ResourceStatus.ASSIGNED if has_links else ResourceStatus.AVAILABLE
class AssignService:
    @staticmethod
    def create_assignment(session, mission_id: str, resource_id: str, note: str | None = None):
        m = session.get(Mission, mission_id)
        if not m:
            raise ValueError("not_found_mission")
        r = session.get(Resource, resource_id)
        if not r:
            raise ValueError("not_found_resource")

        # Unicité garantie par uq_mission_resource
        link = MissionResource(
            mission_id=mission_id,
            resource_id=resource_id,
            assigned_at=datetime.now(timezone.utc),
            note=note
        )
        session.add(link)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            raise ValueError("duplicate_assignment")

        # Après l’assignation, la ressource devient ASSIGNED
        refresh_resource_status(session, resource_id)
        return link

    @staticmethod
    def delete_assignment(session, link_id: str):
        link = session.get(MissionResource, link_id)
        if not link:
            raise ValueError("not_found_link")
        rid = link.resource_id
        session.delete(link)
        session.flush()
        # Après suppression du lien, recalculer le statut de la ressource
        refresh_resource_status(session, rid)
        return True