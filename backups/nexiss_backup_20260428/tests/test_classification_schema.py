"""Tests for classification schema helpers."""
from nexiss.schemas.classification import build_classification_list
from nexiss.db.models.classification import DocumentCategory


def test_build_classification_list_returns_all_12_categories():
    resp = build_classification_list()
    assert len(resp.categories) == len(DocumentCategory)


def test_each_category_has_label_and_subtypes():
    resp = build_classification_list()
    for cat_info in resp.categories:
        assert cat_info.label
        assert len(cat_info.subtypes) >= 1


def test_category_values_are_valid_enum_members():
    resp = build_classification_list()
    values = {c.value for c in DocumentCategory}
    for cat_info in resp.categories:
        assert cat_info.category.value in values
