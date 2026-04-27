"""Pydantic schemas for document classification."""
from __future__ import annotations

from nexiss.db.models.classification import CATEGORY_LABELS, CATEGORY_SUBTYPES, DocumentCategory
from pydantic import BaseModel


class CategoryInfo(BaseModel):
    category: DocumentCategory
    label: str
    subtypes: list[str]


class ClassificationListResponse(BaseModel):
    categories: list[CategoryInfo]


def build_classification_list() -> ClassificationListResponse:
    return ClassificationListResponse(
        categories=[
            CategoryInfo(
                category=cat,
                label=CATEGORY_LABELS[cat],
                subtypes=CATEGORY_SUBTYPES.get(cat, []),
            )
            for cat in DocumentCategory
        ]
    )
