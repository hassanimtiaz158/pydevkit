"""Auto-generated smoke tests by PyDevKit."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path('D:\\pydevkit\\sample_project')))

from example import add_numbers, distance_from_origin, multiply_numbers, normalize_text, unused_discount, unused_slugify


def test_add_numbers_is_callable() -> None:
    """Assert add_numbers can be imported."""
    try:
        assert callable(add_numbers)
    except AssertionError:
        raise


def test_add_numbers_accepts_sample_inputs() -> None:
    """Assert add_numbers accepts representative sample inputs."""
    try:
        add_numbers(1, 1)
    except TypeError as exc:
        raise AssertionError("add_numbers rejected generated sample inputs") from exc


def test_multiply_numbers_is_callable() -> None:
    """Assert multiply_numbers can be imported."""
    try:
        assert callable(multiply_numbers)
    except AssertionError:
        raise


def test_multiply_numbers_accepts_sample_inputs() -> None:
    """Assert multiply_numbers accepts representative sample inputs."""
    try:
        multiply_numbers(1, 1)
    except TypeError as exc:
        raise AssertionError("multiply_numbers rejected generated sample inputs") from exc


def test_normalize_text_is_callable() -> None:
    """Assert normalize_text can be imported."""
    try:
        assert callable(normalize_text)
    except AssertionError:
        raise


def test_normalize_text_accepts_sample_inputs() -> None:
    """Assert normalize_text accepts representative sample inputs."""
    try:
        normalize_text("example")
    except TypeError as exc:
        raise AssertionError("normalize_text rejected generated sample inputs") from exc


def test_unused_discount_is_callable() -> None:
    """Assert unused_discount can be imported."""
    try:
        assert callable(unused_discount)
    except AssertionError:
        raise


def test_unused_discount_accepts_sample_inputs() -> None:
    """Assert unused_discount accepts representative sample inputs."""
    try:
        unused_discount(1.5, 1.5)
    except TypeError as exc:
        raise AssertionError("unused_discount rejected generated sample inputs") from exc


def test_unused_slugify_is_callable() -> None:
    """Assert unused_slugify can be imported."""
    try:
        assert callable(unused_slugify)
    except AssertionError:
        raise


def test_unused_slugify_accepts_sample_inputs() -> None:
    """Assert unused_slugify accepts representative sample inputs."""
    try:
        unused_slugify("example")
    except TypeError as exc:
        raise AssertionError("unused_slugify rejected generated sample inputs") from exc


def test_distance_from_origin_is_callable() -> None:
    """Assert distance_from_origin can be imported."""
    try:
        assert callable(distance_from_origin)
    except AssertionError:
        raise


def test_distance_from_origin_accepts_sample_inputs() -> None:
    """Assert distance_from_origin accepts representative sample inputs."""
    try:
        distance_from_origin(1.5, 1.5)
    except TypeError as exc:
        raise AssertionError("distance_from_origin rejected generated sample inputs") from exc
