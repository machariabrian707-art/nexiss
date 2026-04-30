from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nexiss.db.base import Base  # noqa: E402
from nexiss.db.models import *   # noqa: F401,E402  — registers all models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Override sqlalchemy.url from env if present
database_url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "+pg8000").replace("+psycopg2", "+pg8000")
if database_url:
    # Explicitly force pg8000 dialect
    if "postgresql://" in database_url and "+" not in database_url.split("://")[0]:
        database_url = database_url.replace("postgresql://", "postgresql+pg8000://")
    config.set_main_option("sqlalchemy.url", database_url)



def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
