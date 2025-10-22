from flask import Blueprint, request, jsonify, g, current_app
import bcrypt
from flask.views import View
from services.user_service import ValidUser
from http import HTTPStatus
from sqlalchemy.exc import IntegrityError

users_bp = Blueprint("user", __name__)

@users_bp.route("", methods=["POST"])
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

    # 2) appeler le service
    try:
        user = ValidUser.create_user(g.db, payload)
    except ValueError as e:
        code = str(e)
        status = code_to_status.get(code, HTTPStatus.BAD_REQUEST)
        message = code_to_message.get(code, str(e))
        if status == HTTPStatus.CONFLICT:
            try:
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

    # 3) succès
    return jsonify(user.to_dict()), HTTPStatus.CREATED
