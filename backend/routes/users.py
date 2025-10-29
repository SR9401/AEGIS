from flask import Blueprint, request, jsonify, g, current_app
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError
from services.user_service import ValidUser
from authz import require_auth, require_roles

users_bp = Blueprint("user", __name__)

@users_bp.route("", methods=["POST"])
@require_roles("admin","coordinator")
def create_user_route():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload JSON invalide."}), 400

    code_to_status = {
        "email_taken": HTTPStatus.CONFLICT,
        "email_required": HTTPStatus.BAD_REQUEST,
        "invalid_email": HTTPStatus.BAD_REQUEST,
        "password_required": HTTPStatus.BAD_REQUEST,
        "weak_password": HTTPStatus.BAD_REQUEST,
        "invalid_role": HTTPStatus.BAD_REQUEST,
    }
    code_to_message = {
        "email_taken": "Cet e-mail est deja utilise.",
        "email_required": "Email requis.",
        "invalid_email": "Adresse e-mail invalide.",
        "password_required": "Mot de passe requis.",
        "weak_password": "Mot de passe trop faible.",
        "invalid_role": "Role invalide.",
    }

    try:
        user = ValidUser.create_user(g.db, payload)
    except ValueError as e:
        code = str(e)
        status = code_to_status.get(code, HTTPStatus.BAD_REQUEST)
        message = code_to_message.get(code, str(e))
        try:
            if status == HTTPStatus.CONFLICT:
                g.db.rollback()
        except Exception:
            pass
        return jsonify({"error": code, "message": message}), status
    except IntegrityError:
        try:
            g.db.rollback()
        except Exception:
            pass
        return jsonify({"error": "email_taken", "message": "Cet e-mail est déjà utilisé."}), HTTPStatus.CONFLICT
    except Exception:
        current_app.logger.exception("Erreur création utilisateur")
        return jsonify({"error": "internal_error", "message": "Erreur serveur."}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify(user.to_dict()), HTTPStatus.CREATED


# ---------- LIST ----------
@users_bp.route("", methods=["GET"])
@require_auth
def list_users_route():
    """
    Filtres: ?role=observer&email=john
    Pagination: ?limit=50&offset=0
    """
    role = request.args.get("role")
    email_like = request.args.get("email")
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"error": "bad_request", "message": "limit/offset doivent être des entiers."}), 400

    try:
        items = ValidUser.list_users(g.db, role=role, email_like=email_like, limit=limit, offset=offset)
        return jsonify([u.to_dict() for u in items]), HTTPStatus.OK
    except ValueError as e:
        if str(e) == "invalid_role":
            return jsonify({"error": "invalid_role", "message": "Role invalide."}), HTTPStatus.BAD_REQUEST
        raise
    except Exception:
        current_app.logger.exception("Erreur list users")
        return jsonify({"error": "internal_error", "message": "Erreur serveur."}), HTTPStatus.INTERNAL_SERVER_ERROR


# ---------- GET BY ID ----------
@users_bp.route("/<uid>", methods=["GET"])
@require_auth
def get_user_route(uid):
    try:
        user = ValidUser.get_user(g.db, uid)
        return jsonify(user.to_dict()), HTTPStatus.OK
    except ValueError as e:
        if str(e) == "not_found":
            return jsonify({"error": "not_found", "message": "Utilisateur introuvable."}), HTTPStatus.NOT_FOUND
        raise
    except Exception:
        current_app.logger.exception("Erreur get user")
        return jsonify({"error": "internal_error", "message": "Erreur serveur."}), HTTPStatus.INTERNAL_SERVER_ERROR


# ---------- PATCH ----------
@users_bp.route("/<uid>", methods=["PATCH"])
@require_roles("admin","coordinator")
def update_user_route(uid):
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload JSON invalide."}), 400

    code_to_status = {
        "not_found": HTTPStatus.NOT_FOUND,
        "invalid_role": HTTPStatus.BAD_REQUEST,
        "invalid_email": HTTPStatus.BAD_REQUEST,
        "email_taken": HTTPStatus.CONFLICT,
        "password_required": HTTPStatus.BAD_REQUEST,
        "weak_password": HTTPStatus.BAD_REQUEST,
    }

    try:
        user = ValidUser.update_user(g.db, uid, payload)
        return jsonify(user.to_dict()), HTTPStatus.OK
    except ValueError as e:
        code = str(e)
        status = code_to_status.get(code, HTTPStatus.BAD_REQUEST)
        if code == "email_taken":
            try:
                g.db.rollback()
            except Exception:
                pass
        return jsonify({"error": code, "message": code.replace("_", " ")}), status
    except IntegrityError:
        try:
            g.db.rollback()
        except Exception:
            pass
        return jsonify({"error": "email_taken", "message": "Cet e-mail est déjà utilisé."}), HTTPStatus.CONFLICT
    except Exception:
        current_app.logger.exception("Erreur update user")
        return jsonify({"error": "internal_error", "message": "Erreur serveur."}), HTTPStatus.INTERNAL_SERVER_ERROR


# ---------- DELETE ----------
@users_bp.route("/<uid>", methods=["DELETE"])
@require_roles("admin")
def delete_user_route(uid):
    try:
        ValidUser.delete_user(g.db, uid)
        return jsonify({"ok": True}), HTTPStatus.OK
    except ValueError as e:
        if str(e) == "not_found":
            return jsonify({"error": "not_found", "message": "Utilisateur introuvable."}), HTTPStatus.NOT_FOUND
        raise
    except Exception:
        current_app.logger.exception("Erreur delete user")
        return jsonify({"error": "internal_error", "message": "Erreur serveur."}), HTTPStatus.INTERNAL_SERVER_ERROR