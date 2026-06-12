import pytest
from pydantic import ValidationError

from src.core.security import GetPasswordHash
from src.schemas.requests.auth import LoginRequest, SignUpRequest


def test_signup_request_rejects_password_over_bcrypt_byte_limit():
    long_password = "a" * 73
    with pytest.raises(ValidationError):
        SignUpRequest(login_id="tester", password=long_password)


def test_login_request_rejects_password_over_bcrypt_byte_limit():
    long_password = "a" * 73
    with pytest.raises(ValidationError):
        LoginRequest(login_id="tester", password=long_password)


def test_get_password_hash_raises_for_password_over_bcrypt_byte_limit():
    long_password = "a" * 73
    with pytest.raises(ValueError):
        GetPasswordHash(long_password)


def test_get_password_hash_accepts_password_at_bcrypt_byte_limit():
    hashed = GetPasswordHash("a" * 72)
    assert hashed.startswith("$2")


def test_login_request_accepts_username_alias():
    request = LoginRequest(username="tester", password="pw")
    assert request.login_id == "tester"


def test_signup_request_accepts_email_alias():
    request = SignUpRequest(email="tester@example.com", password="pw")
    assert request.login_id == "tester@example.com"


def test_login_request_strips_login_id_whitespace():
    request = LoginRequest(login_id="  tester  ", password="pw")
    assert request.login_id == "tester"


