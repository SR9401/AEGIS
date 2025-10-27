from enum import Enum
from flask import Blueprint, request, jsonify, g, current_app
from datetime import datetime, timedelta, timezone
import uuid
import jwt
from extensions import bcrypt
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /auth/login
    Body attendu : { "email": "...", "password": "..." }
    Réponse : { access_token, token_type, expires_in, user }
    """
    # -------------------------
    # 1) Lecture et validation basique du JSON
    # -------------------------
    # - get_json(force=True) force la lecture du body comme JSON.
    # - Si le body n'est pas du JSON valide, renvoyer 400.
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "bad_request", "message": "Payload invalide."}), 400

    # Récupérer email et mot de passe depuis le payload.
    # Normaliser l'email : supprimer les espaces et mettre en minuscules.
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    # Vérifier que l'email et le mot de passe sont fournis.
    if not email or not password:
        return jsonify({"error": "bad_request", "message": "email et password requis."}), 400

    # -------------------------
    # 2) Récupérer la session DB
    # -------------------------
    # La session est ouverte dans app.before_request et stockée dans g.db.
    session = g.get("db")
    if session is None:
        # Si la session n'existe pas, c'est une erreur serveur.
        return jsonify({"error": "internal_error", "message": "DB session non initialisée."}), 500

    # -------------------------
    # 3) Recherche de l'utilisateur en base
    # -------------------------
    # - Chercher l'utilisateur par email (stocké en lowercase dans la base).
    # - Ne pas dire si l'email n'existe pas (message générique pour la sécurité).
    user = session.query(User).filter_by(email=email).first()
    invalid_resp = ({"error": "invalid_credentials", "message": "Identifiants invalides."}, 401)

    if not user:
        # Email inconnu -> renvoyer message générique.
        return invalid_resp

    # -------------------------
    # 4) Vérification du mot de passe
    # -------------------------
    # - bcrypt.check_password_hash(attendu_hash, mot_de_passe_en_clair)
    # - Si la vérification échoue, renvoyer le même message générique.
    try:
        ok = bcrypt.check_password_hash(user.password_hash, password)
    except Exception:
        # Si bcrypt plante pour une raison inattendue, traiter comme un échec d'authentification.
        return invalid_resp

    if not ok:
        # Mot de passe incorrect.
        return invalid_resp

    # -------------------------
    # 5) Vérifier que le compte est actif (si le champ existe)
    # -------------------------
    # - Si le modèle a is_active et que le compte est désactivé, bloquer l'accès.
    if hasattr(user, "is_active") and not user.is_active:
        return jsonify({"error": "forbidden", "message": "Compte inactif."}), 403

    # -------------------------
    # 6) Construire le JWT
    # -------------------------
    # - iat = issued at, exp = expiration, jti = identifiant unique du token
    _raw_role = getattr(user, "role", None)
    if isinstance(_raw_role, Enum):
        # Enum Python -> utiliser name (ou .value si tu stockes des valeurs utiles)
        role_str = _raw_role.name
    elif hasattr(_raw_role, "value"):
        # SQLAlchemy Enum wrapper parfois expose .value
        role_str = str(_raw_role.value)
    else:
        role_str = str(_raw_role) if _raw_role is not None else None

    now = datetime.now(timezone.utc)
    ttl = int(current_app.config.get("JWT_EXPIRES_IN", 900))
    exp = now + timedelta(seconds=ttl)

    claims = {
        "sub": str(user.id),
        "role": role_str,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": str(uuid.uuid4()),
    }

    # récupérer le secret depuis la config de l'app (fallback sur JWT_SECRET si présent)
    secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("JWT_SECRET")
    if not secret:
        # en dev on peut renvoyer une 500 claire ; en prod on devrait fail-fast à l'initialisation
        return jsonify({"error": "internal_error", "message": "JWT secret non configuré."}), 500

    algo = current_app.config.get("JWT_ALGO", "HS256")
    # signer le token (PyJWT peut renvoyer str ou bytes selon la version)
    token = jwt.encode(claims, secret, algorithm=algo)
    # PyJWT v1 renvoyait bytes, v2 renvoie str — normaliser en str pour la réponse JSON
    if isinstance(token, bytes):
        token = token.decode("utf-8")


    # préparer le snapshot utilisateur (role aussi en string)
    user_snapshot = {
        "id": str(user.id),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "role": role_str,
    }
    resp = {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": ttl,
        "user": user_snapshot,
    }

    # -------------------------
    # 9) Retourner la réponse
    # -------------------------
    return jsonify(resp), 200
