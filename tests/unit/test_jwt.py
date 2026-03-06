import pytest
from epicevents.auth.jwt import generate_token, decode_token

def test_generate_token_returns_string(fake_user):
    token = generate_token(fake_user)

    assert isinstance(token, str)


def test_decode_token_returns_payload(fake_user):
    token = generate_token(fake_user)
    payload = decode_token(token)

    assert payload["user_id"] == fake_user.id


def test_decode_token_invalid_token():
    with pytest.raises(Exception):
        decode_token("invalid.token.value")


def test_decode_token_expired(monkeypatch, fake_user):
    from epicevents.auth import jwt as jwt_module

    monkeypatch.setattr(jwt_module, "TOKEN_EXPIRATION_HOURS", -1)

    token = generate_token(fake_user)

    with pytest.raises(Exception):
        decode_token(token)