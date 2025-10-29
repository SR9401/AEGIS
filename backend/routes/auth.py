from enum import Enum
from flask import Blueprint, request, jsonify, g, current_app
from datetime import datetime, timedelta, timezone
import uuid
import jwt
from extensions import bcrypt
from models.user import User

auth_bp = Blueprint("auth", __name__)

def _json_error(code: int, error: str, message: str):
    return jsonify({"error": error, "message": message}), code

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /auth/login
    Body: { "email": "...", "password": "..." }
    Response: { access_token, token_type, expires_in, user }
    """
    # 1) Lire le payload JSON
    try:
        payload = request.get_json(force=True)
    except Exception:
        return _json_error(400, "bad_request", "Payload invalide (JSON attendu).")

    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return _json_error(400, "bad_request", "email et password requis.")

    # 2) Récupérer la session DB (fourni par app.before_request)
    session = getattr(g, "db", None)
    if session is None:
        return _json_error(500, "internal_error", "DB session non initialisée.")

    # 3) Chercher l'utilisateur
    user = session.query(User).filter_by(email=email).first()
    invalid_resp = _json_error(401, "invalid_credentials", "Identifiants invalides.")
    if not user:
        return invalid_resp

    # 4) Vérifier le mot de passe
    try:
        ok = bcrypt.check_password_hash(user.password_hash, password)
    except Exception:
        return invalid_resp
    if not ok:
        return invalid_resp

    # 5) Compte actif (si champ présent)
    if hasattr(user, "is_active") and not user.is_active:
        return _json_error(403, "forbidden", "Compte inactif.")

    # 6) Construire le JWT
    raw_role = getattr(user, "role", None)
    if isinstance(raw_role, Enum):
        role_str = raw_role.value if hasattr(raw_role, "value") else raw_role.name
    else:
        role_str = str(raw_role) if raw_role is not None else None

    now = datetime.now(timezone.utc)
    ttl = int(current_app.config.get("JWT_EXPIRES_IN", 12 * 3600))  # 12h par défaut
    exp = now + timedelta(seconds=ttl)

    claims = {
        "sub": str(user.id),
        "role": role_str,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": str(uuid.uuid4()),
    }

    secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("JWT_SECRET")
    if not secret:
        return _json_error(500, "internal_error", "JWT secret non configuré.")
    algo = current_app.config.get("JWT_ALGO", "HS256")

    token = jwt.encode(claims, secret, algorithm=algo)
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    user_snapshot = {
        "id": str(user.id),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "role": role_str,
        "email": user.email,
    }

    return jsonify({
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": ttl,
        "user": user_snapshot,
    }), 200


# ----------- Endpoint de vérification du token -------------
@auth_bp.route("/me", methods=["GET"])
def me():
    """
    GET /auth/me
    Header: Authorization: Bearer <token>
    -> Retourne les claims + un snapshot user
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return _json_error(401, "unauthorized", "Header Authorization Bearer manquant.")

    token = auth.split(" ", 1)[1].strip()
    secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("JWT_SECRET")
    if not secret:
        return _json_error(500, "internal_error", "JWT secret non configuré.")
    algo = current_app.config.get("JWT_ALGO", "HS256")

    try:
        claims = jwt.decode(token, secret, algorithms=[algo])
    except jwt.ExpiredSignatureError:
        return _json_error(401, "token_expired", "Le token a expiré.")
    except jwt.InvalidTokenError:
        return _json_error(401, "invalid_token", "Token invalide.")

    # Optionnel: recharger l'utilisateur pour renvoyer un snapshot
    session = getattr(g, "db", None)
    user = session.get(User, claims.get("sub")) if session else None

    return jsonify({
        "claims": claims,
        "user": user.to_dict() if user else None
    }), 200
