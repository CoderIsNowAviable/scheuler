import os
from dotenv import load_dotenv
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.models import Base  # Import your SQLAlchemy Base where the models are defined


load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")


if not isinstance(SQLALCHEMY_DATABASE_URL, str):
    raise ValueError("SQLALCHEMY_DATABASE_URL must be a valid string.")
# Alembic Config object, providing access to values in the .ini file
config = context.config
config.set_section_option("alembic", "sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to the Base.metadata of your models
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (without connecting to the DB)."""
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
    """Run migrations in 'online' mode (with a database connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Run migrations based on whether we're in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
