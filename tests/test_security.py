from uuid import uuid4

from nexiss.core.security import create_access_token, decode_token, get_password_hash, verify_password


def test_password_hash_and_verify() -> None:
    raw = "StrongPass123!"
    hashed = get_password_hash(raw)

    assert hashed != raw
    assert verify_password(raw, hashed)
    assert not verify_password("bad-password", hashed)


def test_access_token_encode_decode() -> None:
    user_id = uuid4()
    org_id = uuid4()
    token = create_access_token(user_id=user_id, org_id=org_id)
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["org_id"] == str(org_id)
    assert payload["type"] == "access"
