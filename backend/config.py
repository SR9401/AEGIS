import os

# NOTE :
# - En développement, on accepte des valeurs par défaut pratiques.
# - En production, il faut définir les variables d'environnement correspondantes
#   (par ex. JWT_SECRET_KEY, SECRET_KEY, DATABASE_URL, ...).
# - Le démarrage en production sans JWT_SECRET_KEY doit être empêché par app.py
#   (fail-fast). Ici on fournit juste les valeurs lues depuis l'environnement.

class Config:
    """Configuration de base (valeurs par défaut raisonnables pour dev)."""
    # Clé Flask (sessions, CSRF si utilisé). Changez en prod.
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    # Secret pour signer les JWT. En dev on met une valeur par défaut,
    # mais en production il faut fournir une vraie valeur via l'env.
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret")
    # Algorithme JWT (HS256 est courant)
    JWT_ALGO = os.getenv("JWT_ALGO", "HS256")
    # Durée de vie du token d'accès en secondes (par défaut 15 minutes)
    JWT_EXPIRES_IN = int(os.getenv("JWT_EXPIRES_IN", 900))

    # bcrypt work factor (valeur basse en dev pour accélérer les tests)
    BCRYPT_LOG_ROUNDS = int(os.getenv("BCRYPT_LOG_ROUNDS", 6))

    # Throttling / anti-bruteforce (login) — réglages par défaut pour dev
    RATE_LIMIT_LOGIN = int(os.getenv("RATE_LIMIT_LOGIN", 5))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 300))  # secondes

    # SQLAlchemy (vide ici, surchargé par les environnements)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", None)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Debug par défaut désactivé dans la config de base
    DEBUG = False


class DevelopmentConfig(Config):
    """Configuration pour le développement local."""
    DEBUG = True
    # DB locale légère pour dev; changez si vous préférez Postgres en local.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///development.db")
    # En développement, on baisse les rounds bcrypt pour gagner du temps
    BCRYPT_LOG_ROUNDS = int(os.getenv("BCRYPT_LOG_ROUNDS", 6))


class ProductionConfig(Config):
    """Configuration pour la production."""
    DEBUG = False
    # En prod, on attend une URL DB fournie via l'environnement.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
    # En prod, augmenter le coût bcrypt (12+ recommandé)
    BCRYPT_LOG_ROUNDS = int(os.getenv("BCRYPT_LOG_ROUNDS", 12))
   


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
