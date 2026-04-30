"""Organization model.

Fix: removed the redundant `id` primary key column.
The Organization table used BOTH `id` (PK) and `org_id` (unique) which caused
SQLAlchemy flush ordering issues — FK references to `org_id` from `users` and
`org_memberships` were failing on register because `org_id` had a Python-side
`default` but no DB `server_default`, so it wasn't guaranteed to be populated
before the FK columns were evaluated.

Now `org_id` IS the primary key, matching every FK that references it.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from nexiss.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
