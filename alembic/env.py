from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # -> AEGIS/
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# --- Alembic config ---
config = context.config

# Logging depuis alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from backend.db import Base
from backend.models.user import User
from backend.models.mission import Mission
from backend.models.resource import Resource
from backend.models.mission_resource import MissionResource

target_metadata = Base.metadata

db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
