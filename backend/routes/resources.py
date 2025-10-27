from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from backend.db import SessionLocal
from backend.models import Resource, ResourceStatus
# from backend.auth import jwt_required, current_user, require_roles  # si tu as déjà ces helpers

bp_resources = Blueprint("resources", __name__, url_prefix="/resources")

def parse_status(value):
    if value is None:
        return None
    try:
        return ResourceStatus(value)
    except ValueError:
        return None

@bp_resources.route("", methods=["POST"])
# @jwt_required()
# @require_roles("admin", "coordinator")
def create_resource():
    data = request.get_json(force=True) or {}
    required = ["name", "type"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    status = parse_status(data.get("status")) or ResourceStatus.AVAILABLE
    try:
        quantity = float(data.get("quantity", 1.0))
        if quantity < 0:
            raise ValueError()
    except Exception:
        return jsonify({"error": "quantity must be a non-negative number"}), 400

    db = SessionLocal()
    try:
        r = Resource(
            name=data["name"].strip(),
            type=data["type"].strip(),
            quantity=quantity,
            unit=(data.get("unit") or None),
            status=status,
            location=(data.get("location") or None),
            created_by=(data.get("created_by") or "system"),  # remplace par current_user.id si tu as JWT
        )
        db.add(r)
        db.commit()
        db.refresh(r)
        return jsonify(r.to_dict()), 201
    except IntegrityError as e:
        db.rollback()
        return jsonify({"error": "Integrity error", "detail": str(e)}), 409
    finally:
        db.close()

@bp_resources.route("", methods=["GET"])
# @jwt_required()
def list_resources():
    db = SessionLocal()
    try:
        q = db.query(Resource)
        if "status" in request.args:
            st = parse_status(request.args.get("status"))
            if st:
                q = q.filter(Resource.status == st)
        if "type" in request.args:
            q = q.filter(Resource.type == request.args["type"])
        if "name" in request.args:
            q = q.filter(Resource.name.ilike(f"%{request.args['name']}%"))
        items = [r.to_dict() for r in q.all()]
        return jsonify(items), 200
    finally:
        db.close()

@bp_resources.route("/<rid>", methods=["GET"])
# @jwt_required()
def get_resource(rid):
    db = SessionLocal()
    try:
        r = db.get(Resource, rid)
        if not r:
            return jsonify({"error": "Resource not found"}), 404
        return jsonify(r.to_dict()), 200
    finally:
        db.close()

@bp_resources.route("/<rid>", methods=["PATCH"])
# @jwt_required()
# @require_roles("admin", "coordinator")
def update_resource(rid):
    data = request.get_json(force=True) or {}
    db = SessionLocal()
    try:
        r = db.get(Resource, rid)
        if not r:
            return jsonify({"error": "Resource not found"}), 404

        if "name" in data and data["name"]:
            r.name = data["name"].strip()
        if "type" in data and data["type"]:
            r.type = data["type"].strip()
        if "quantity" in data:
            try:
                qv = float(data["quantity"])
                if qv < 0:
                    raise ValueError()
                r.quantity = qv
            except Exception:
                return jsonify({"error": "quantity must be a non-negative number"}), 400
        if "unit" in data:
            r.unit = data["unit"] or None
        if "status" in data:
            st = parse_status(data["status"])
            if not st:
                return jsonify({"error": "invalid status"}), 400
            r.status = st
        if "location" in data:
            r.location = data["location"] or None

        r.save()
        db.add(r)
        db.commit()
        db.refresh(r)
        return jsonify(r.to_dict()), 200
    finally:
        db.close()

@bp_resources.route("/<rid>", methods=["DELETE"])
# @jwt_required()
# @require_roles("admin", "coordinator")
def delete_resource(rid):
    db = SessionLocal()
    try:
        r = db.get(Resource, rid)
        if not r:
            return jsonify({"error": "Resource not found"}), 404

        # TODO: bloquer si ressource encore assignée (MissionResource existe)
        # count = db.query(MissionResource).filter_by(resource_id=rid).count()
        # if count > 0: return jsonify({"error": "Resource is assigned"}), 409

        db.delete(r)
        db.commit()
        return jsonify({"ok": True}), 200
    finally:
        db.close()
