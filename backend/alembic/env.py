from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from src.domain.models.db_models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
