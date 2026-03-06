import pytest
from epicevents.auth.jwt import generate_token, decode_token


class FakeUser:
    """
    Simple object to simulate a Collaborator.
    Only has an id attribute as tokens are only concerned with the user id
    """
    def __init__(self, user_id):
        self.id = user_id


def test_generate_token_returns_string():
    user = FakeUser(1)

    token = generate_token(user)

    assert isinstance(token, str)


def test_decode_token_returns_payload():
    user = FakeUser(42)

    token = generate_token(user)
    payload = decode_token(token)

    assert payload["user_id"] == 42


def test_decode_token_invalid_token():
    with pytest.raises(Exception):
        decode_token("invalid.token.value")


def test_decode_token_expired(monkeypatch):
    from epicevents.auth import jwt as jwt_module

    user = FakeUser(1)

    monkeypatch.setattr(jwt_module, "TOKEN_EXPIRATION_HOURS", -1)

    token = generate_token(user)

    with pytest.raises(Exception):
        decode_token(token)