"""Unit tests for auth helpers: hash_password, verify_password, create_access_token."""
import pytest
from app.auth import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt


def test_hash_password_produces_bcrypt_hash():
    h = hash_password("mysecret")
    assert h.startswith("$2b$")


def test_verify_password_correct():
    h = hash_password("correct")
    assert verify_password("correct", h) is True


def test_verify_password_wrong():
    h = hash_password("correct")
    assert verify_password("wrong", h) is False


def test_create_access_token_contains_sub():
    token = create_access_token(42)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "42"


def test_create_access_token_has_expiry():
    token = create_access_token(1)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload
