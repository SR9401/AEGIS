from flask import Blueprint, request, jsonify, g, current_app
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError
from models.resource import Resource, ResourceStatus
from authz import require_auth, require_roles
from sqlalchemy import exists
from models.mission_resource import MissionResource
resources_bp = Blueprint("resource", __name__)

def _parse_status(value: str | None) -> ResourceStatus:
    if not value:
        return ResourceStatus.AVAILABLE
    try:
        return ResourceStatus(value.strip().lower())
    except Exception:
        raise ValueError("invalid_status")

@resources_bp.route("", methods=["POST"])
@require_roles("admin","coordinator")
def create_resource_route():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload JSON invalide."}), HTTPStatus.BAD_REQUEST

    # ✅ label officiel ; on tolère "name" pour compat
    label = (data.get("label") or data.get("name") or "").strip()
    rtype = (data.get("type") or "").strip()
    if not rtype or not label:
        missing = []
        if not rtype: missing.append("type")
        if not label: missing.append("label")  # <— pas "name"
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), HTTPStatus.BAD_REQUEST

    try:
        status = _parse_status(data.get("status"))
    except ValueError:
        return jsonify({"error": "invalid_status", "message": "Status invalide (available|assigned|maintenance)"}), 400

    res = Resource(type=rtype, label=label, status=status, details=data.get("details"))
    try:
        g.db.add(res)
        g.db.flush()  # commit géré ailleurs si tu as un teardown ; sinon g.db.commit()
    except IntegrityError:
        g.db.rollback()
        return jsonify({"error": "conflict", "message": "label déjà utilisé"}), 409
    except Exception:
        current_app.logger.exception("Erreur création ressource")
        return jsonify({"error": "internal_error"}), 500

    return jsonify(res.to_dict()), HTTPStatus.CREATED

@resources_bp.route("", methods=["GET"])
@require_auth
def list_resources_route():
    status_q = request.args.get("status")
    type_q = request.args.get("type")
    label_q = request.args.get("label")
    q = g.db.query(Resource)
    try:
        if status_q:
            q = q.filter(Resource.status == _parse_status(status_q))
    except ValueError:
        return jsonify({"error": "invalid_status"}), 400
    if type_q:
        q = q.filter(Resource.type == type_q)
    if label_q:
        q = q.filter(Resource.label.ilike(f"%{label_q}%"))
    items = [r.to_dict() for r in q.order_by(Resource.created_at.desc()).all()]
    return jsonify(items), 200

@resources_bp.route("/<rid>", methods=["GET"])
@require_auth
def get_resource_route(rid):
    r = g.db.get(Resource, rid)
    if not r:
        return jsonify({"error": "not_found"}), 404
    return jsonify(r.to_dict()), 200

@resources_bp.route("/<rid>", methods=["PATCH"])
@require_roles("admin","coordinator")
def update_resource_route(rid):
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "bad_request"}), 400

    r = g.db.get(Resource, rid)
    if not r:
        return jsonify({"error": "not_found"}), 404

    if "type" in data and data["type"] is not None:
        r.type = str(data["type"]).strip() or r.type

    if "label" in data or "name" in data:
        new_label = (data.get("label") or data.get("name") or "").strip()
        if not new_label:
            return jsonify({"error": "bad_request", "message": "label ne peut pas être vide"}), 400
        r.label = new_label

    if "status" in data:
        try:
            r.status = _parse_status(data.get("status"))
        except ValueError:
            return jsonify({"error": "invalid_status"}), 400

    if "details" in data:
        r.details = data.get("details")

    try:
        g.db.flush()
    except IntegrityError:
        g.db.rollback()
        return jsonify({"error": "conflict", "message": "label déjà utilisé"}), 409
    return jsonify(r.to_dict()), 200

@resources_bp.route("/<rid>", methods=["DELETE"])
@require_roles("admin","coordinator")
@require_roles("admin", "coordinator")
def delete_resource(rid):
    r = g.db.get(Resource, rid)
    if not r:
        return jsonify({"error": "not_found"}), 404

    # Refuser la suppression si encore assignée à au moins une mission
    is_linked = g.db.query(
        exists().where(MissionResource.resource_id == rid)
    ).scalar()
    if is_linked or r.status == ResourceStatus.ASSIGNED:
        return jsonify({"error": "conflict", "message": "Resource still assigned to a mission."}), 409

    try:
        g.db.delete(r)
        g.db.flush()
        return jsonify({"ok": True}), 200
    except Exception:
        g.db.rollback()
        return jsonify({"error": "internal_error"}), 500