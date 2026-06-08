# example.py

def add_numbers(left: int, right: int) -> int:
    """
    Add two integers and return the total.
    
    Args:
        left (int): The first number.
        right (int): The second number.
    
    Returns:
        int: The total sum of left and right.
    """
    return left + right

def multiply_numbers(left: int, right: int) -> int:
    """
    Multiply two integers and return the product.
    
    Args:
        left (int): The first number.
        right (int): The second number.
    
    Returns:
        int: The product of left and right.
    """
    return left * right

def normalize_text(value: str) -> str:
    """
    Normalize whitespace and lowercase a string.
    
    Args:
        value (str): The string to be normalized.
    
    Returns:
        str: The normalized string.
    """
    return value.strip().lower()

def unused_discount(price: float, percent: float) -> float:
    """
    Calculate a discounted price.
    
    Args:
        price (float): The original price.
        percent (float): The discount percentage.
    
    Returns:
        float: The discounted price.
    """
    return price - (price * percent / 100)

def unused_slugify(value: str) -> str:
    """
    Convert a phrase into a simple URL slug.
    
    Args:
        value (str): The string to be slugified.
    
    Returns:
        str: The slugified string.
    """
    return ''.join(e for e in value if e.isalnum()).lower()

def distance_from_origin(x_value: float, y_value: float) -> float:
    """
    Calculate distance from the origin for a point.
    
    Args:
        x_value (float): The X-coordinate of the point.
        y_value (float): The Y-coordinate of the point.
    
    Returns:
        float: The distance from the origin.
    """
    return (x_value ** 2 + y_value ** 2) ** 0.5
