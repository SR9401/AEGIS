# backend/routes/missions.py
from flask import Blueprint, request, jsonify, g
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional

from authz import require_auth, require_roles
from models.mission import Mission, Status
from services.assign_service import AssignService

missions_bp = Blueprint("missions", __name__)

# ----------------- Helpers -----------------

def _parse_status(value: Optional[str]) -> Optional[Status]:
    if value is None:
        return None
    v = value.strip().lower()
    try:
        return Status(v)
    except Exception:
        raise ValueError("invalid_status")

def _parse_iso_datetime(s: Optional[str]) -> Optional[datetime]:
    """Accepte: '2025-11-15T09:00:00Z' ou '2025-11-15T09:00:00+00:00' ou date seule '2025-11-15' (à 00:00:00 UTC)."""
    if not s:
        return None
    txt = s.strip()
    if not txt:
        return None
    try:
        if txt.endswith("Z"):
            txt = txt.replace("Z", "+00:00")
        # date seule -> minuit UTC
        if len(txt) == 10 and txt.count("-") == 2:
            txt = txt + "T00:00:00+00:00"
        return datetime.fromisoformat(txt)
    except Exception:
        raise ValueError("invalid_datetime")

def _float_or_none(x):
    if x is None or str(x).strip() == "":
        return None
    try:
        return float(x)
    except Exception:
        raise ValueError("invalid_float")

def _pagination_args():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        if page < 1 or limit < 1:
            raise ValueError
    except Exception:
        raise ValueError("invalid_pagination")
    offset = (page - 1) * limit
    return page, limit, offset

# ----------------- Routes -----------------

@missions_bp.route("", methods=["POST"])
@require_roles("admin", "coordinator")
def create_mission():
    """Créer une mission"""
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload JSON invalide."}), 400

    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "bad_request", "message": "title requis"}), 400

    description = data.get("description")
    try:
        status = _parse_status(data.get("status")) or Status.PLANNED
    except ValueError:
        return jsonify({"error": "invalid_status", "message": "Status invalide (planned|active|done)"}), 400

    try:
        date = _parse_iso_datetime(data.get("date"))
    except ValueError:
        return jsonify({"error": "invalid_date", "message": "date ISO invalide"}), 400

    try:
        lat = _float_or_none(data.get("lat"))
        lon = _float_or_none(data.get("lon"))
    except ValueError:
        return jsonify({"error": "bad_request", "message": "lat/lon doivent être numériques"}), 400

    created_by = (data.get("created_by") or "").strip()
    if not created_by:
        return jsonify({"error": "bad_request", "message": "created_by requis"}), 400

    m = Mission(
        title=title,
        description=description,
        status=status,
        date=date,
        lat=lat,
        lon=lon,
        created_by=created_by,
    )
    try:
        g.db.add(m)
        g.db.flush()
    except IntegrityError:
        g.db.rollback()
        return jsonify({"error": "conflict"}), 409

    return jsonify(m.to_dict()), HTTPStatus.CREATED


@missions_bp.route("", methods=["GET"])
@require_auth
def list_missions():
    """
    Liste paginée + filtres:
      - status=planned|active|done
      - search=mot (dans title ou description)
      - date_from=YYYY-MM-DD[THH:MM:SSZ]
      - date_to=YYYY-MM-DD[THH:MM:SSZ]
      - created_by=<user_id>
      - page, limit
    Réponse: { items:[...], page, limit, total }
    """
    q = g.db.query(Mission)

    # Filtres
    status_str = request.args.get("status")
    if status_str:
        try:
            q = q.filter(Mission.status == _parse_status(status_str))
        except ValueError:
            return jsonify({"error": "invalid_status", "message": "Status invalide (planned|active|done)"}), 400

    search = request.args.get("search")
    if search:
        like = f"%{search}%"
        q = q.filter((Mission.title.ilike(like)) | (Mission.description.ilike(like)))

    try:
        df = _parse_iso_datetime(request.args.get("date_from"))
        dt = _parse_iso_datetime(request.args.get("date_to"))
    except ValueError:
        return jsonify({"error": "invalid_date", "message": "date_from/date_to invalides"}), 400

    if df:
        q = q.filter(Mission.date >= df)
    if dt:
        q = q.filter(Mission.date <= dt)

    created_by = request.args.get("created_by")
    if created_by:
        q = q.filter(Mission.created_by == created_by.strip())

    # Pagination
    try:
        page, limit, offset = _pagination_args()
    except ValueError:
        return jsonify({"error": "bad_request", "message": "page/limit doivent être >= 1"}), 400

    total = q.count()
    items = q.order_by(Mission.created_at.desc()).limit(limit).offset(offset).all()

    return jsonify({
        "items": [m.to_dict() for m in items],
        "page": page,
        "limit": limit,
        "total": total,
    }), 200


@missions_bp.route("/<mid>", methods=["GET"])
@require_auth
def get_mission(mid):
    m = g.db.get(Mission, mid)
    if not m:
        return jsonify({"error": "not_found"}), 404
    return jsonify(m.to_dict()), 200


@missions_bp.route("/<mid>", methods=["PATCH"])
@require_roles("admin", "coordinator")
def update_mission(mid):
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload JSON invalide."}), 400

    m = g.db.get(Mission, mid)
    if not m:
        return jsonify({"error": "not_found"}), 404

    if "title" in data:
        t = (data.get("title") or "").strip()
        if not t:
            return jsonify({"error": "bad_request", "message": "title ne peut pas être vide"}), 400
        m.title = t

    if "description" in data:
        m.description = data.get("description")

    if "status" in data:
        try:
            m.status = _parse_status(data.get("status")) or m.status
        except ValueError:
            return jsonify({"error": "invalid_status", "message": "Status invalide (planned|active|done)"}), 400

    if "date" in data:
        try:
            m.date = _parse_iso_datetime(data.get("date"))
        except ValueError:
            return jsonify({"error": "invalid_date"}), 400

    if "lat" in data:
        try:
            m.lat = _float_or_none(data.get("lat"))
        except ValueError:
            return jsonify({"error": "bad_request", "message": "lat invalide"}), 400

    if "lon" in data:
        try:
            m.lon = _float_or_none(data.get("lon"))
        except ValueError:
            return jsonify({"error": "bad_request", "message": "lon invalide"}), 400

    if "created_by" in data:
        cb = (data.get("created_by") or "").strip()
        if not cb:
            return jsonify({"error": "bad_request", "message": "created_by ne peut pas être vide"}), 400
        m.created_by = cb

    try:
        g.db.flush()
    except IntegrityError:
        g.db.rollback()
        return jsonify({"error": "conflict"}), 409

    return jsonify(m.to_dict()), 200


@missions_bp.route("/<mid>", methods=["DELETE"])
@require_roles("admin", "coordinator")
def delete_mission(mid):
    m = g.db.get(Mission, mid)
    if not m:
        return jsonify({"error": "not_found"}), 404

    try:
        g.db.delete(m)
        g.db.flush()
    except Exception:
        g.db.rollback()
        return jsonify({"error": "internal_error"}), 500

    return jsonify({"ok": True}), 200



@missions_bp.route("/<mid>/assign", methods=["POST"])
@require_roles("admin", "coordinator")
def assign_resource_alias(mid):
    """
    Body: { "resource_id": "...", "note": "..."? }
    -> Réutilise la logique du service d'assignation.
    """
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload JSON invalide"}), 400

    resource_id = (data.get("resource_id") or "").strip()
    note = data.get("note")

    if not resource_id:
        return jsonify({"error": "bad_request", "message": "resource_id requis"}), 400

    try:
        link = AssignService.create_assignment(g.db, mission_id=mid, resource_id=resource_id, note=note)
        return jsonify(link.to_dict()), HTTPStatus.CREATED
    except ValueError as e:
        code = str(e)
        if code == "not_found_mission":
            return jsonify({"error": code, "message": "Mission introuvable"}), 404
        if code == "not_found_resource":
            return jsonify({"error": code, "message": "Ressource introuvable"}), 404
        if code == "duplicate_assignment":
            return jsonify({"error": code, "message": "Ressource déjà assignée à cette mission"}), 409
        return jsonify({"error": "internal_error"}), 500
