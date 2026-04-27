"""Shared test utilities."""
from typing import Any


def assert_keys(data: dict, *keys: str) -> None:
    """Assert that all given keys exist in a dict."""
    for key in keys:
        assert key in data, f"Missing key: {key}"


def make_user_payload(suffix: str = "") -> dict[str, Any]:
    return {
        "email": f"user{suffix}@nexiss.io",
        "password": "password123",
        "full_name": f"Test User {suffix}",
        "org_name": f"Org {suffix}",
    }
