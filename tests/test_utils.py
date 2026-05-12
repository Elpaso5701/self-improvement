import pytest
from utils import add, multiply, validate_email, count_words, reverse_string, is_palindrome

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(0, 100) == 0

def test_validate_email():
    assert validate_email("test@mail.com") == True
    assert validate_email("invalid.com") == False

def test_count_words():
    assert count_words("hello world test") == 3

def test_reverse_string():
    assert reverse_string("hello") == "olleh"

def test_is_palindrome():
    assert is_palindrome("A man, a plan, a canal, Panama") == True
    assert is_palindrome("hello") == False
    assert is_palindrome("racecar") == True
    assert is_palindrome("No 'x' in Nixon") == True
    assert is_palindrome("") == True  # Empty string is a palindrome