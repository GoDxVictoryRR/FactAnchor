from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys

# Add backend dir to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    url = os.getenv("DATABASE_URL_SYNC")
    if not url:
        url = os.getenv("DATABASE_URL", "")
        url = url.replace("+asyncpg", "")
    if not url:
        url = (
            f"postgresql://{os.getenv('POSTGRES_USER', 'factanchor_app')}:"
            f"{os.getenv('POSTGRES_PASSWORD', 'CHANGE_ME_STRONG_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST', 'pgbouncer')}:"
            f"{os.getenv('POSTGRES_PORT', '5432')}/"
            f"{os.getenv('POSTGRES_DB', 'factanchor')}"
        )
    return url

def run_migrations_offline():
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
