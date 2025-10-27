from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from db import SessionLocal
from models.mission import Mission
from models.resource import Resource, ResourceStatus
from models.mission_resource import MissionResource

assign_bp = Blueprint("assign", __name__, url_prefix="/assign")

@assign_bp.route("", methods=["POST"])
# @jwt_required()
# @require_roles("admin", "coordinator")
def assign_resource():
    data = request.get_json(force=True) or {}
    for f in ("mission_id", "resource_id", "quantity"):
        if f not in data:
            return jsonify({"error": f"Missing field: {f}"}), 400
    try:
        qty = float(data["quantity"])
        if qty <= 0:
            raise ValueError()
    except Exception:
        return jsonify({"error": "quantity must be a positive number"}), 400

    db = SessionLocal()
    try:
        m = db.get(Mission, data["mission_id"])
        r = db.get(Resource, data["resource_id"])
        if not m or not r:
            return jsonify({"error": "Mission or Resource not found"}), 404

        # Vérifier stock disponible (simple : compare à r.quantity)
        if qty > r.quantity:
            return jsonify({"error": "Insufficient resource quantity"}), 409

        link = db.query(MissionResource).filter_by(
            mission_id=m.id, resource_id=r.id
        ).one_or_none()

        if link:
            # mise à jour quantité
            new_qty = link.quantity_allocated + qty
            if new_qty <= 0:
                return jsonify({"error": "resulting quantity must be > 0"}), 400
            link.quantity_allocated = new_qty
        else:
            link = MissionResource(
                mission_id=m.id,
                resource_id=r.id,
                quantity_allocated=qty
            )
            db.add(link)

        # Décrémenter le stock de la ressource
        r.quantity = r.quantity - qty
        if r.quantity <= 0:
            r.status = ResourceStatus.IN_USE

        db.commit()
        db.refresh(link)
        return jsonify(link.to_dict()), 201
    except IntegrityError as e:
        db.rollback()
        return jsonify({"error": "Integrity error", "detail": str(e)}), 409
    finally:
        db.close()

@assign_bp.route("/mission/<mid>", methods=["GET"])
# @jwt_required()
def list_assignments_for_mission(mid):
    db = SessionLocal()
    try:
        items = db.query(MissionResource).filter_by(mission_id=mid).all()
        return jsonify([i.to_dict() for i in items]), 200
    finally:
        db.close()

@assign_bp.route("/<aid>", methods=["PATCH"])
# @jwt_required()
# @require_roles("admin", "coordinator")
def update_assignment(aid):
    data = request.get_json(force=True) or {}
    if "quantity" not in data:
        return jsonify({"error": "Missing field: quantity"}), 400
    try:
        new_qty = float(data["quantity"])
    except Exception:
        return jsonify({"error": "quantity must be a number"}), 400
    if new_qty <= 0:
        return jsonify({"error": "quantity must be > 0"}), 400

    db = SessionLocal()
    try:
        link = db.get(MissionResource, aid)
        if not link:
            return jsonify({"error": "Assignment not found"}), 404

        r = db.get(Resource, link.resource_id)
        if not r:
            return jsonify({"error": "Resource not found"}), 404

        # Calcul delta
        delta = new_qty - link.quantity_allocated
        # Si delta > 0, il faut plus de stock
        if delta > 0 and delta > r.quantity:
            return jsonify({"error": "Insufficient resource quantity"}), 409

        # Applique
        link.quantity_allocated = new_qty
        r.quantity = r.quantity - delta
        r.status = ResourceStatus.IN_USE if r.quantity <= 0 else r.status

        db.commit()
        db.refresh(link)
        return jsonify(link.to_dict()), 200
    finally:
        db.close()

@assign_bp.route("/<aid>", methods=["DELETE"])
# @jwt_required()
# @require_roles("admin", "coordinator")
def delete_assignment(aid):
    db = SessionLocal()
    try:
        link = db.get(MissionResource, aid)
        if not link:
            return jsonify({"error": "Assignment not found"}), 404

        r = db.get(Resource, link.resource_id)
        if not r:
            return jsonify({"error": "Resource not found"}), 404

        # Réintègre le stock
        r.quantity = r.quantity + link.quantity_allocated
        if r.quantity > 0 and r.status == ResourceStatus.IN_USE:
            r.status = ResourceStatus.AVAILABLE

        db.delete(link)
        db.commit()
        return jsonify({"ok": True}), 200
    finally:
        db.close()
