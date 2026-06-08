"""Auto-generated smoke tests by PyDevKit."""

import sys
from pathlib import Path

PROJECT_ROOT = str(Path('D:\\pydevkit\\sample_project'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from example import add_numbers, distance_from_origin, multiply_numbers, normalize_text, unused_discount, unused_slugify


def test_add_numbers_is_callable() -> None:
    """Assert add_numbers can be imported."""
    assert callable(add_numbers)


def test_multiply_numbers_is_callable() -> None:
    """Assert multiply_numbers can be imported."""
    assert callable(multiply_numbers)


def test_normalize_text_is_callable() -> None:
    """Assert normalize_text can be imported."""
    assert callable(normalize_text)


def test_unused_discount_is_callable() -> None:
    """Assert unused_discount can be imported."""
    assert callable(unused_discount)


def test_unused_slugify_is_callable() -> None:
    """Assert unused_slugify can be imported."""
    assert callable(unused_slugify)


def test_distance_from_origin_is_callable() -> None:
    """Assert distance_from_origin can be imported."""
    assert callable(distance_from_origin)
