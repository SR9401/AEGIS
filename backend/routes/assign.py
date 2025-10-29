from flask import Blueprint, request, jsonify, g, current_app
from http import HTTPStatus
from models.mission_resource import MissionResource
from models.mission import Mission
from models.resource import Resource, ResourceStatus
from sqlalchemy.exc import IntegrityError
from authz import require_auth, require_roles

assign_bp = Blueprint("assign", __name__)

@assign_bp.route("", methods=["POST"])
@require_roles("admin","coordinator")
def create_assignment():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload JSON invalide"}), 400

    mission_id = (data.get("mission_id") or "").strip()
    resource_id = (data.get("resource_id") or "").strip()
    note = data.get("note")

    missing = [k for k, v in [("mission_id", mission_id), ("resource_id", resource_id)] if not v]
    if missing:
        return jsonify({"error": f"Missing field: {missing[0]}"}), 400

    # Vérifie existence mission/ressource
    m = g.db.get(Mission, mission_id)
    if not m:
        return jsonify({"error": "not_found", "message": "Mission introuvable"}), 404

    r = g.db.get(Resource, resource_id)
    if not r:
        return jsonify({"error": "not_found", "message": "Ressource introuvable"}), 404

    # Empêcher le doublon (contrainte unique mission_id+resource_id existe déjà)
    link = MissionResource(mission_id=mission_id, resource_id=resource_id, note=note or None)
    try:
        g.db.add(link)

        # Met la ressource en 'assigned' (optionnel selon ta logique)
        if r.status != ResourceStatus.ASSIGNED:
            r.status = ResourceStatus.ASSIGNED
            g.db.add(r)

        g.db.flush()  # ou commit si pas de middleware
    except IntegrityError:
        g.db.rollback()
        return jsonify({"error": "conflict", "message": "Cette ressource est déjà assignée à cette mission"}), 409
    except Exception:
        g.db.rollback()
        current_app.logger.exception("Erreur création assignation")
        return jsonify({"error": "internal_error"}), 500

    return jsonify(link.to_dict()), HTTPStatus.CREATED

@assign_bp.route("/mission/<mission_id>", methods=["GET"])
@require_auth
def list_assignments_for_mission(mission_id):
    items = g.db.query(MissionResource).filter_by(mission_id=mission_id).all()
    return jsonify([i.to_dict() for i in items]), 200

@assign_bp.route("/<assign_id>", methods=["DELETE"])
@require_roles("admin","coordinator")
def delete_assignment(assign_id):
    link = g.db.get(MissionResource, assign_id)
    if not link:
        return jsonify({"error": "not_found"}), 404

    # Optionnel: remettre la ressource en available si plus aucune assignation
    res = g.db.get(Resource, link.resource_id)

    try:
        g.db.delete(link)
        g.db.flush()

        if res:
            remaining = g.db.query(MissionResource).filter_by(resource_id=res.id).count()
            if remaining == 0 and res.status == ResourceStatus.ASSIGNED:
                res.status = ResourceStatus.AVAILABLE
                g.db.add(res)
                g.db.flush()
    except Exception:
        g.db.rollback()
        return jsonify({"error": "internal_error"}), 500

    return jsonify({"ok": True}), 200