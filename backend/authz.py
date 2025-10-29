from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def _decode_bearer():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise ValueError("missing_bearer")
    token = auth.split(" ", 1)[1].strip()
    secret = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("JWT_SECRET")
    algo = current_app.config.get("JWT_ALGO", "HS256")
    claims = jwt.decode(token, secret, algorithms=[algo])
    return claims

def require_auth(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        try:
            claims = _decode_bearer()
        except jwt.ExpiredSignatureError:
            return jsonify({"error":"token_expired"}), 401
        except Exception:
            return jsonify({"error":"invalid_token"}), 401
        g.jwt = claims
        g.user_id = claims.get("sub")
        g.role = (claims.get("role") or "").lower()
        return fn(*a, **kw)
    return wrapper

def require_roles(*roles):
    allowed = {r.lower() for r in roles}
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            resp = require_auth(lambda *x, **y: None)(*a, **kw)
            if resp is not None:
                return resp
            if (g.role or "") not in allowed:
                return jsonify({"error":"forbidden","message":"insufficient role"}), 403
            return fn(*a, **kw)
        return wrapper
    return deco