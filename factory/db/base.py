"""Declarative base + shared column types."""

from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase

# JSONB on Postgres, plain JSON elsewhere (keeps tooling/tests portable).
JSONType = JSON().with_variant(JSONB, "postgresql")


class Base(DeclarativeBase):
    pass
