"""initial schema

Baseline migration: builds the full schema from the SQLAlchemy models so it can
never drift from the ORM. Subsequent migrations should be created with
`alembic revision --autogenerate -m "..."`.

Revision ID: 0001_initial
Revises:
"""

from __future__ import annotations

from alembic import op

from factory.db import models  # noqa: F401  (registers tables on Base.metadata)
from factory.db.base import Base

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(op.get_bind())
