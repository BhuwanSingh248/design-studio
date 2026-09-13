"""Init pgvector extension and knowledge_chunks table

Revision ID: xxxx_pgvector_init
"""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector;")
