"""Entity matching service.

When the LLM extracts a name like 'Doshi Traders Ltd' from a document,
this service:
  1. Looks for an exact match in canonical_name or entity_aliases.
  2. Falls back to fuzzy token-sort matching (difflib, no extra deps).
  3. If score >= threshold  → links to existing entity.
  4. If score < threshold   → queues the candidate for human review
     (stored in entity_aliases with a 'review:' prefix flag).
  5. If no entity exists at all → creates a new one.

All operations are org-scoped. Nothing leaks across tenants.
"""
from __future__ import annotations

import difflib
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.db.models.entity import DocumentEntity, Entity, EntityAlias

# If a fuzzy score is >= this value we consider it a confident match
_FUZZY_THRESHOLD = 0.82
# Prefix used to mark aliases that are pending human confirmation
_REVIEW_PREFIX = "review:"


@dataclass(slots=True)
class MatchResult:
    entity_id: uuid.UUID
    canonical_name: str
    score: float
    is_new: bool
    needs_review: bool


def _normalize(name: str) -> str:
    """Lowercase, strip extra spaces — cheap normalisation before comparison."""
    return " ".join(name.lower().split())


def _fuzzy_score(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


class EntityMatchingService:
    """Resolves raw extracted names to canonical entities within an org."""

    async def resolve(
        self,
        db: AsyncSession,
        *,
        org_id: uuid.UUID,
        raw_name: str,
        entity_kind: str = "unknown",
    ) -> MatchResult:
        """Return a MatchResult, creating or linking entities as needed."""
        norm = _normalize(raw_name)

        # 1. Exact canonical match
        exact = await db.execute(
            select(Entity).where(
                Entity.org_id == org_id,
                Entity.canonical_name == norm,
            )
        )
        entity = exact.scalar_one_or_none()
        if entity is not None:
            return MatchResult(
                entity_id=entity.id,
                canonical_name=entity.canonical_name,
                score=1.0,
                is_new=False,
                needs_review=False,
            )

        # 2. Exact alias match
        alias_row = await db.execute(
            select(EntityAlias)
            .join(Entity, EntityAlias.entity_id == Entity.id)
            .where(
                Entity.org_id == org_id,
                EntityAlias.alias == norm,
            )
        )
        alias = alias_row.scalar_one_or_none()
        if alias is not None:
            parent = await db.get(Entity, alias.entity_id)
            return MatchResult(
                entity_id=alias.entity_id,
                canonical_name=parent.canonical_name if parent else norm,
                score=1.0,
                is_new=False,
                needs_review=False,
            )

        # 3. Fuzzy scan over all org entities + aliases
        all_entities = (await db.execute(
            select(Entity).where(Entity.org_id == org_id)
        )).scalars().all()

        best_score = 0.0
        best_entity: Entity | None = None

        for ent in all_entities:
            s = _fuzzy_score(raw_name, ent.canonical_name)
            if s > best_score:
                best_score = s
                best_entity = ent

        # Also check aliases for fuzzy hits
        all_aliases = (await db.execute(
            select(EntityAlias)
            .join(Entity, EntityAlias.entity_id == Entity.id)
            .where(
                Entity.org_id == org_id,
                ~EntityAlias.alias.startswith(_REVIEW_PREFIX),
            )
        )).scalars().all()

        for al in all_aliases:
            s = _fuzzy_score(raw_name, al.alias)
            if s > best_score:
                best_score = s
                parent = await db.get(Entity, al.entity_id)
                best_entity = parent

        if best_entity is not None and best_score >= _FUZZY_THRESHOLD:
            # Confident fuzzy match — add as confirmed alias
            db.add(EntityAlias(entity_id=best_entity.id, alias=norm))
            await db.flush()
            return MatchResult(
                entity_id=best_entity.id,
                canonical_name=best_entity.canonical_name,
                score=best_score,
                is_new=False,
                needs_review=False,
            )

        if best_entity is not None and best_score >= 0.60:
            # Low-confidence — create entity but flag for review
            new_entity = Entity(org_id=org_id, canonical_name=norm, entity_kind=entity_kind)
            db.add(new_entity)
            await db.flush()
            # Save the candidate match as a review alias so admins can merge
            db.add(EntityAlias(
                entity_id=new_entity.id,
                alias=f"{_REVIEW_PREFIX}{best_entity.id}",
            ))
            await db.flush()
            return MatchResult(
                entity_id=new_entity.id,
                canonical_name=norm,
                score=best_score,
                is_new=True,
                needs_review=True,
            )

        # 4. No match — create brand-new entity
        new_entity = Entity(org_id=org_id, canonical_name=norm, entity_kind=entity_kind)
        db.add(new_entity)
        await db.flush()
        return MatchResult(
            entity_id=new_entity.id,
            canonical_name=norm,
            score=0.0,
            is_new=True,
            needs_review=False,
        )

    async def link_to_document(
        self,
        db: AsyncSession,
        *,
        org_id: uuid.UUID,
        document_id: uuid.UUID,
        entity_id: uuid.UUID,
        role: str | None = None,
    ) -> None:
        """Create a document→entity edge (idempotent)."""
        existing = await db.execute(
            select(DocumentEntity).where(
                DocumentEntity.document_id == document_id,
                DocumentEntity.entity_id == entity_id,
                DocumentEntity.role == role,
            )
        )
        if existing.scalar_one_or_none() is None:
            db.add(DocumentEntity(
                org_id=org_id,
                document_id=document_id,
                entity_id=entity_id,
                role=role,
            ))
            await db.flush()
