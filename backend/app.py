# backend/app.py
import os
from flask import Flask, g
from flask_cors import CORS

from db import Base, engine, SessionLocal
from extensions import bcrypt

# Blueprints
from routes.auth import auth_bp
from routes.users import users_bp
from routes.missions import missions_bp
from routes.resources import resources_bp
from routes.assign import assign_bp

# (optionnel) config objets si tu en as un module config/
try:
    import config
except ImportError:
    config = None

def create_app():
    app = Flask(__name__)

    # ---- Config ----
    env = os.getenv("FLASK_ENV", "development")
    if config and hasattr(config, "config"):
        app.config.from_object(config.config.get(env, getattr(config, "DevelopmentConfig", object)))
    # Valeurs par défaut utiles si pas de module config
    app.config.setdefault("JWT_SECRET_KEY", os.getenv("JWT_SECRET", "dev-secret-change-me"))
    app.config.setdefault("JWT_EXPIRES_IN", 12 * 3600)  # 12h
    app.config.setdefault("JWT_ALGO", "HS256")

    # ---- CORS ----
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    CORS(
        app,
        resources={r"/*": {"origins": [
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
    	]}},
        supports_credentials=False,
        expose_headers=["Content-Type"],
        allow_headers=["Content-Type", "Authorization", "X-User-Id"],
    )

    # ---- Extensions ----
    bcrypt.init_app(app)

    # ---- DB schema (DEV uniquement) ----
    if env == "development":
        with app.app_context():
            Base.metadata.create_all(bind=engine)  # en prod, utiliser Alembic

    # ---- Session DB par requête ----
    @app.before_request
    def open_session():
        g.db = SessionLocal()

    @app.teardown_request
    def close_session(exc):
        db = getattr(g, "db", None)
        if db is None:
            return
        try:
            if exc is None:
                db.commit()
            else:
                db.rollback()
        finally:
            db.close()

    # ---- Blueprints ----
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(missions_bp, url_prefix="/missions")
    app.register_blueprint(resources_bp, url_prefix="/resources")
    app.register_blueprint(assign_bp, url_prefix="/assign")

    @app.get("/health")
    def health():
        return {"ok": True, "env": env}, 200

    return app


app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug)
