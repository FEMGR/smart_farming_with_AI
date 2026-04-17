from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import os
import sys

# 🔥 Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 🔥 Import config + Base
from app.core.config import DATABASE_URL
from app.database.db import Base

# 🔥 Import ALL models (critical for autogenerate)
from app.models.plant import Plant
from app.models.location import Location
from app.models.user import User
from app.models.notification import Notification
from app.models.plant_action import PlantAction
from app.models.plant_group import PlantGroup
from app.models.plant_growth import PlantGrowth
from app.models.soil_condition import SoilCondition
from app.models.plant_species_cache import PlantSpeciesCache

config = context.config

# 🔥 Inject DB URL from config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ===============================
# OFFLINE MODE
# ===============================
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ===============================
# ONLINE MODE
# ===============================
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 🔥 detects column changes
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
