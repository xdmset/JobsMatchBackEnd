import sys
from os import path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Aseguramos que el proyecto sea importable
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from app.db.base import Base # Aquí ya están todos tus modelos importados
from app.core.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online() -> None:
    # Sobreescribimos la URL del .ini con la de nuestro .env
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Llamada según el modo
if context.is_offline_mode():
    # Implementar run_migrations_offline si se requiere, 
    # por ahora usaremos solo online
    pass
else:
    run_migrations_online()