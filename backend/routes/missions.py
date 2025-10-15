from flask import Blueprint, request, jsonify, g
from sqlalchemy.exc import IntegrityError

from services.mission_service import create_mission, update_mission, delete_mission, get_missions

missions_bp = Blueprint("missions", __name__)

# POST /missions
@missions_bp.route("", methods=["POST"])
def create_mission_route():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload JSON invalide."}), 400

    # provisoire : récupérer created_by depuis header si pas d'auth
    created_by = request.headers.get("X-User-Id") or payload.get("created_by")
    if not created_by:
        return jsonify({"error": "bad_request", "message": "created_by requis."}), 400

    try:
        m = create_mission(g.db, payload, created_by, verify_creator=False)
    except ValueError as e:
        return jsonify({"error": "validation_error", "message": str(e)}), 400
    except IntegrityError as e:
        # conflit DB (ex: contrainte unique)
        return jsonify({"error": "conflict", "message": "Conflit en base."}), 409
    except Exception as e:
        return jsonify({"error": "internal_error", "message": "Erreur serveur."}), 500

    return jsonify(m.to_dict()), 201


# GET /missions  (liste + filtres + pagination)
"""@missions_bp.route("", methods=["GET"])
def list_missions_route():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    filters = {
        "status": request.args.get("status"),
        "date_from": request.args.get("date_from"),
        "date_to": request.args.get("date_to"),
    }
    data = list_missions(g.db, filters, page=page, per_page=per_page, sort=request.args.get("sort", "date_desc"))
    return jsonify({
        "items": [m.to_dict() for m in data["items"]],
        "meta": data["meta"]
    }), 200
"""

# GET /missions/<id>
@missions_bp.route("/<mission_id>", methods=["GET"])
def get_mission_route(mission_id):
    m = get_missions(g.db, mission_id)
    if not m:
        return jsonify({"error": "not_found", "message": "Mission introuvable."}), 404
    return jsonify(m.to_dict()), 200


# PATCH /missions/<id>
@missions_bp.route("/<mission_id>", methods=["PATCH"])
def patch_mission_route(mission_id):
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload JSON invalide."}), 400

    m = update_mission(g.db, mission_id, payload)
    if not m:
        return jsonify({"error": "not_found", "message": "Mission introuvable."}), 404
    return jsonify(m.to_dict()), 200


# DELETE /missions/<id>
@missions_bp.route("/<mission_id>", methods=["DELETE"])
def delete_mission_route(mission_id):
    ok = delete_mission(g.db, mission_id, soft=True)
    if not ok:
        return jsonify({"error": "not_found", "message": "Mission introuvable."}), 404
    return "", 204
