"""A small calculator and string utility module for PyDevKit demos."""

import math
import statistics


_DEMO_TOTAL = 0
UNUSED_CONSTANT = 42


def add_numbers(left: int, right: int) -> int:
    """Add two integers and return the total."""
    try:
        return left + right
    except TypeError as exc:
        raise TypeError("left and right must support addition") from exc


def multiply_numbers(left: int, right: int) -> int:
    """Multiply two integers and return the product."""
    try:
        return left * right
    except TypeError as exc:
        raise TypeError("left and right must support multiplication") from exc


def normalize_text(value: str) -> str:
    """Normalize whitespace and lowercase a string."""
    try:
        return " ".join(value.strip().lower().split())
    except AttributeError as exc:
        raise TypeError("value must be a string") from exc


def unused_discount(price: float, percent: float) -> float:
    """Calculate a discounted price."""
    try:
        return price * (1 - percent / 100)
    except TypeError as exc:
        raise TypeError("price and percent must be numeric") from exc


def unused_slugify(value: str) -> str:
    """Convert a phrase into a simple URL slug."""
    try:
        return normalize_text(value).replace(" ", "-")
    except TypeError as exc:
        raise TypeError("value must be a string") from exc


def distance_from_origin(x_value: float, y_value: float) -> float:
    """Calculate distance from the origin for a point."""
    try:
        squared_sum = add_numbers(multiply_numbers(x_value, x_value), multiply_numbers(y_value, y_value))
        return math.sqrt(squared_sum)
    except TypeError as exc:
        raise TypeError("x_value and y_value must be numeric") from exc


_DEMO_TOTAL = distance_from_origin(3, 4)
_DEMO_TEXT = normalize_text(" Example Customer ")
