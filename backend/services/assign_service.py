# backend/services/assign_service.py
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError
from models.mission_resource import MissionResource
from models.mission import Mission
from models.resource import Resource, ResourceStatus

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
