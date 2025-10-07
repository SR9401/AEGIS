from db import Base, engine
from flask import Flask, g
from db import SessionLocal
from routes.auth import auth_bp
from routes.users import users_bp
from routes.missions import missions_bp
from routes.resources import resources_bp
from routes.assign import assign_bp
from extensions import bcrypt 
import os
import config

app = Flask(__name__)

env = os.getenv("FLASK_ENV", "development")
app.config.from_object(config.config.get(env, config.DevelopmentConfig))

bcrypt.init_app(app)
with app.app_context():
	Base.metadata.create_all(bind=engine)

@app.before_request
def create_session():
    g.db = SessionLocal()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db = g.pop("db", None)
    if db is not None:
        if exception:
            db.rollback()
        else:
            db.commit()
        db.close()


app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(missions_bp, url_prefix="/missions")
app.register_blueprint(resources_bp, url_prefix="/resources")
app.register_blueprint(assign_bp, url_prefix="/assign")

if __name__ == "__main__":
    app.run(debug=True)
