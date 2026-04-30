from uuid import uuid4

import pytest
from fastapi import HTTPException

from nexiss.api.v1.documents import _assert_org_storage_key


def test_assert_org_storage_key_accepts_org_prefixed_key() -> None:
    org_id = uuid4()
    _assert_org_storage_key(f"{org_id}/raw/doc.pdf", org_id)


def test_assert_org_storage_key_rejects_mismatched_org_prefix() -> None:
    org_id = uuid4()
    other = uuid4()
    with pytest.raises(HTTPException):
        _assert_org_storage_key(f"{other}/raw/doc.pdf", org_id)
