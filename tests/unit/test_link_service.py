import pytest
from app.services.link_service import generate_short_code


def test_length_default():
    code = generate_short_code()
    assert len(code) == 6


def test_length_custom():
    code = generate_short_code(10)
    assert len(code) == 10


def test_alphanumeric():
    code = generate_short_code()
    assert code.isalnum()


def test_uniqueness():
    codes = {generate_short_code() for _ in range(1000)}
    assert len(codes) == 1000


def test_zero_length():
    code = generate_short_code(0)
    assert code == ""
