"""Entity registry service.

Handles:
- Resolving entity names from extracted_data per document type
- Upserting entities + aliases (fuzzy deduplication via pg_trgm or simple Python difflib)
- Linking documents to their entities
- Search: find documents by entity name + optional doc_type filter
"""
from __future__ import annotations

import difflib
import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.db.models.document import Document
from nexiss.db.models.entity import DocumentEntity, Entity, EntityAlias


# ---------------------------------------------------------------------------
# Name extraction helpers — pull entity names from structured extracted_data
# ---------------------------------------------------------------------------

_FIELD_MAP: dict[str, list[tuple[str, str]]] = {
    # doc_type -> list of (field_path, entity_kind, role)
    "invoice":        [("vendor_name",    "organization")],
    "receipt":        [("vendor_name",    "organization")],
    "quotation":      [("vendor_name",    "organization")],
    "purchase_order": [("vendor_name",    "organization")],
    "patient_record": [("patient_name",   "person"), ("doctor_name", "person")],
    "prescription":   [("patient_name",   "person"), ("doctor_name", "person")],
    "lab_result":     [("patient_name",   "person"), ("doctor_name", "person")],
    "medical_report": [("patient_name",   "person"), ("doctor_name", "person")],
    "contract":       [("parties",        "organization")],
    "agreement":      [("parties",        "organization")],
    "cv_resume":      [("full_name",       "person")],
    "employee_record":[("employee_name",   "person")],
    "offer_letter":   [("employee_name",   "person")],
    "national_id":    [("full_name",       "person")],
    "passport":       [("full_name",       "person")],
    "bill_of_lading": [("shipper",         "organization"), ("consignee", "organization")],
    "bank_statement": [("account_holder",  "person")],
}


def _extract_names(doc_type: str, extracted_data: dict) -> list[tuple[str, str]]:
    """Return list of (name, entity_kind) tuples from extracted_data."""
    results: list[tuple[str, str]] = []
    for field, kind in _FIELD_MAP.get(doc_type, []):
        value = extracted_data.get(field)
        if not value:
            continue
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip():
                    results.append((item.strip(), kind))
        elif isinstance(value, str) and value.strip():
            results.append((value.strip(), kind))
    return results


# ---------------------------------------------------------------------------
# Fuzzy matching
# ---------------------------------------------------------------------------

def _is_similar(a: str, b: str, threshold: float = 0.85) -> bool:
    ratio = difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
    return ratio >= threshold


# ---------------------------------------------------------------------------
# Main service
# ---------------------------------------------------------------------------

class EntityService:
    async def link_document_entities(
        self,
        db: AsyncSession,
        document: Document,
    ) -> None:
        """Extract entity names from document.extracted_data, upsert entities, link to doc."""
        doc_type = document.confirmed_type or document.declared_type or "unknown"
        if not document.extracted_data:
            return

        name_kind_pairs = _extract_names(doc_type, document.extracted_data)
        if not name_kind_pairs:
            return

        for name, kind in name_kind_pairs:
            entity = await self._upsert_entity(db, document.org_id, name, kind)
            await self._link_doc_to_entity(db, document, entity, role=kind)

        await db.commit()

    async def _upsert_entity(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        name: str,
        kind: str,
    ) -> Entity:
        """Find existing entity (exact or fuzzy match via aliases), or create new."""
        # Exact canonical match
        result = await db.execute(
            select(Entity).where(
                Entity.org_id == org_id,
                Entity.canonical_name == name,
                Entity.entity_kind == kind,
            )
        )
        entity = result.scalar_one_or_none()
        if entity:
            return entity

        # Check aliases
        alias_result = await db.execute(
            select(EntityAlias).where(EntityAlias.alias == name)
        )
        alias = alias_result.scalar_one_or_none()
        if alias:
            entity_result = await db.execute(
                select(Entity).where(Entity.id == alias.entity_id)
            )
            entity = entity_result.scalar_one_or_none()
            if entity and entity.org_id == org_id:
                return entity

        # Fuzzy scan (only scan entities of same org + kind)
        all_entities = await db.execute(
            select(Entity).where(Entity.org_id == org_id, Entity.entity_kind == kind)
        )
        for existing in all_entities.scalars():
            if _is_similar(existing.canonical_name, name):
                # Register as alias so future lookups are faster
                await self._add_alias(db, existing.id, name)
                return existing

        # Create new entity
        entity = Entity(org_id=org_id, canonical_name=name, entity_kind=kind)
        db.add(entity)
        await db.flush()  # get id
        return entity

    @staticmethod
    async def _add_alias(db: AsyncSession, entity_id: uuid.UUID, alias: str) -> None:
        existing = await db.execute(
            select(EntityAlias).where(
                EntityAlias.entity_id == entity_id,
                EntityAlias.alias == alias,
            )
        )
        if existing.scalar_one_or_none() is None:
            db.add(EntityAlias(entity_id=entity_id, alias=alias))

    @staticmethod
    async def _link_doc_to_entity(
        db: AsyncSession,
        document: Document,
        entity: Entity,
        role: str | None,
    ) -> None:
        existing = await db.execute(
            select(DocumentEntity).where(
                DocumentEntity.document_id == document.id,
                DocumentEntity.entity_id == entity.id,
                DocumentEntity.role == role,
            )
        )
        if existing.scalar_one_or_none() is None:
            db.add(
                DocumentEntity(
                    org_id=document.org_id,
                    document_id=document.id,
                    entity_id=entity.id,
                    role=role,
                )
            )

    async def search(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        query: str,
        doc_type: str | None = None,
        limit: int = 50,
    ) -> Sequence[Document]:
        """Find documents whose entities match the query string."""
        # Find matching entity ids (canonical name or alias)
        entity_ids: list[uuid.UUID] = []

        # Exact + fuzzy match on canonical names
        all_entities = await db.execute(
            select(Entity).where(Entity.org_id == org_id)
        )
        for entity in all_entities.scalars():
            if _is_similar(entity.canonical_name, query, threshold=0.6):
                entity_ids.append(entity.id)

        # Also check aliases
        all_aliases = await db.execute(
            select(EntityAlias)
        )
        for alias in all_aliases.scalars():
            if _is_similar(alias.alias, query, threshold=0.6):
                # Get the entity
                e_res = await db.execute(
                    select(Entity).where(
                        Entity.id == alias.entity_id,
                        Entity.org_id == org_id,
                    )
                )
                e = e_res.scalar_one_or_none()
                if e and e.id not in entity_ids:
                    entity_ids.append(e.id)

        if not entity_ids:
            return []

        doc_ids_result = await db.execute(
            select(DocumentEntity.document_id).where(
                DocumentEntity.org_id == org_id,
                DocumentEntity.entity_id.in_(entity_ids),
            ).distinct()
        )
        doc_ids = [r[0] for r in doc_ids_result]

        q = select(Document).where(
            Document.org_id == org_id,
            Document.id.in_(doc_ids),
        )
        if doc_type:
            q = q.where(Document.confirmed_type == doc_type)
        q = q.order_by(Document.created_at.desc()).limit(limit)

        result = await db.execute(q)
        return result.scalars().all()
