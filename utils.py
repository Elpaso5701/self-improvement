def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The sum of a and b.
    """
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The product of a and b.
    """
    return a * b

def validate_email(email: str) -> bool:
    """Validate an email address.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    return "@" in email and "." in email.split("@")[-1]

def count_words(text: str) -> int:
    """Count the number of words in a given text.

    Args:
        text (str): The text to count words in.

    Returns:
        int: The number of words in the text.
    """
    return len(text.split())

def reverse_string(s: str) -> str:
    """Reverse a given string.

    Args:
        s (str): The string to reverse.

    Returns:
        str: The reversed string.
    """
    return s[::-1]

def is_palindrome(s: str) -> bool:
    """Check if a given string is a palindrome.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string is a palindrome, False otherwise.
    """
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]