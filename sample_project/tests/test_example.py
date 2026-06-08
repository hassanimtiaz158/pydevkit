def add_numbers(left: int, right: int) -> int:
    """
    Add two integers and return the total.
    """
    return left + right


def multiply_numbers(left: int, right: int) -> int:
    """
    Multiply two integers and return the product.
    """
    return left * right


def normalize_text(value: str) -> str:
    """
    Normalize whitespace and lowercase a string.
    """
    return value.strip().lower()


def unused_discount(price: float, percent: float) -> float:
    """
    Calculate a discounted price.
    """
    return price - (price * percent / 100)


def unused_slugify(value: str) -> str:
    """
    Convert a phrase into a simple URL slug.
    """
    return value.replace(" ", "-").lower()


def distance_from_origin(x_value: float, y_value: float) -> float:
    """
    Calculate distance from the origin for a point.
    """
    return ((x_value ** 2) + (y_value ** 2)) ** 0.5
