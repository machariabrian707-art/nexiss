from uuid import uuid4

import pytest

from nexiss.services.storage import s3_service


def test_validate_content_type_accepts_supported_types() -> None:
    s3_service.validate_content_type("application/pdf")
    s3_service.validate_content_type("image/png")
    s3_service.validate_content_type("image/jpeg")


def test_validate_content_type_rejects_unsupported_type() -> None:
    with pytest.raises(ValueError):
        s3_service.validate_content_type("text/plain")


def test_build_storage_key_scopes_key_to_org() -> None:
    org_id = uuid4()
    key = s3_service.build_storage_key(org_id, "../../evil.pdf")

    assert key.startswith(f"{org_id}/raw/")
    assert key.endswith("-evil.pdf")


def test_create_upload_url_uses_presigned_put(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def generate_presigned_url(self, ClientMethod: str, Params: dict, ExpiresIn: int) -> str:  # noqa: N803
            captured["method"] = ClientMethod
            captured["params"] = Params
            captured["expires"] = ExpiresIn
            return "https://example.local/upload"

    monkeypatch.setattr(s3_service, "get_s3_client", lambda: FakeClient())
    url = s3_service.create_upload_url("org-a/raw/file.pdf", "application/pdf")

    assert url == "https://example.local/upload"
    assert captured["method"] == "put_object"
    assert captured["params"] == {
        "Bucket": s3_service.settings.s3_bucket,
        "Key": "org-a/raw/file.pdf",
        "ContentType": "application/pdf",
    }
    assert captured["expires"] == s3_service.settings.s3_presign_expiry_seconds


def test_create_download_url_uses_presigned_get(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def generate_presigned_url(self, ClientMethod: str, Params: dict, ExpiresIn: int) -> str:  # noqa: N803
            captured["method"] = ClientMethod
            captured["params"] = Params
            captured["expires"] = ExpiresIn
            return "https://example.local/download"

    monkeypatch.setattr(s3_service, "get_s3_client", lambda: FakeClient())
    url = s3_service.create_download_url("org-a/raw/file.pdf")

    assert url == "https://example.local/download"
    assert captured["method"] == "get_object"
    assert captured["params"] == {
        "Bucket": s3_service.settings.s3_bucket,
        "Key": "org-a/raw/file.pdf",
    }
    assert captured["expires"] == s3_service.settings.s3_presign_expiry_seconds
