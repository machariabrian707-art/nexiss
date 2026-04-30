from decimal import Decimal

from nexiss.api.v1.usage import _normalize_total_cost


def test_normalize_total_cost_preserves_none() -> None:
    assert _normalize_total_cost(None) is None


def test_normalize_total_cost_preserves_decimal_value() -> None:
    value = Decimal("12.340000")
    assert _normalize_total_cost(value) == value
