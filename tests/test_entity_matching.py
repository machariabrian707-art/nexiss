"""Tests for entity matching service (fuzzy deduplication, alias creation, review queue)."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nexiss.services.entity.matching import (
    EntityMatchingService,
    MatchResult,
    _fuzzy_score,
    _normalize,
)


# ---- Unit tests: pure functions ----

def test_normalize_lowercases_and_collapses_spaces():
    assert _normalize("  Doshi   Traders  ") == "doshi traders"


def test_fuzzy_score_identical_strings():
    assert _fuzzy_score("doshi traders", "doshi traders") == 1.0


def test_fuzzy_score_similar_strings():
    score = _fuzzy_score("Doshi Traders Ltd", "Doshi Traders")
    assert score > 0.7


def test_fuzzy_score_unrelated_strings():
    score = _fuzzy_score("apple", "zebra")
    assert score < 0.5


# ---- Integration-style tests using mocked DB ----

def _make_entity(name: str, org_id: uuid.UUID) -> MagicMock:
    e = MagicMock()
    e.id = uuid.uuid4()
    e.canonical_name = name
    e.org_id = org_id
    e.entity_kind = "organization"
    return e


@pytest.mark.asyncio
async def test_resolve_creates_new_entity_when_no_match():
    service = EntityMatchingService()
    org_id = uuid.uuid4()
    db = AsyncMock()

    # Simulate no exact match, no aliases, no existing entities
    db.execute = AsyncMock()
    # exact canonical query
    db.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)
    # alias query
    db.execute.return_value.scalar_one_or_none = MagicMock(return_value=None)

    # scalars().all() for fuzzy scan returns empty
    scalars_mock = MagicMock()
    scalars_mock.all = MagicMock(return_value=[])
    db.execute.return_value.scalars = MagicMock(return_value=scalars_mock)

    new_entity = _make_entity("brand new vendor", org_id)
    db.flush = AsyncMock()
    db.add = MagicMock()

    with patch(
        "nexiss.services.entity.matching.Entity",
        return_value=new_entity,
    ):
        result = await service.resolve(
            db, org_id=org_id, raw_name="Brand New Vendor", entity_kind="organization"
        )

    assert isinstance(result, MatchResult)
    assert result.is_new is True


def test_match_result_fields():
    entity_id = uuid.uuid4()
    result = MatchResult(
        entity_id=entity_id,
        canonical_name="doshi traders",
        score=0.95,
        is_new=False,
        needs_review=False,
    )
    assert result.entity_id == entity_id
    assert result.needs_review is False
    assert result.score == 0.95
