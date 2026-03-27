import pytest

from tests.conftest import FakeSession, FakeUser
from epicevents.auth.current_user import get_current_user
from epicevents.models.collaborator import Collaborator
from epicevents.exceptions import NotLoggedInError, InvalidAuthTokenError, UserNotFoundError


def raise_invalid_token(token):
    raise InvalidAuthTokenError("Invalid token")


def test_get_current_user_no_token(monkeypatch):
    monkeypatch.setattr("epicevents.auth.current_user.load_token", lambda: None)

    with pytest.raises(NotLoggedInError, match="You are not logged in"):
        get_current_user()


def test_get_current_user_invalid_token(monkeypatch):
    monkeypatch.setattr("epicevents.auth.current_user.load_token", lambda: "fake-token")
    monkeypatch.setattr("epicevents.auth.current_user.decode_token", raise_invalid_token)

    with pytest.raises(InvalidAuthTokenError, match="Invalid token"):
        get_current_user()


def test_get_current_user_user_deleted(monkeypatch):
    session = FakeSession(query_map={Collaborator: []})

    monkeypatch.setattr("epicevents.auth.current_user.load_token", lambda: "token")
    monkeypatch.setattr("epicevents.auth.current_user.decode_token", lambda token: {"user_id": 1})
    monkeypatch.setattr("epicevents.auth.current_user.SessionLocal", lambda: session)

    with pytest.raises(UserNotFoundError, match="User no longer exists"):
        get_current_user()

    assert session.closed is True


def test_get_current_user_success(monkeypatch):
    user = FakeUser(user_id=1, role_name="MANAGEMENT")
    session = FakeSession(query_map={Collaborator: [user]})

    monkeypatch.setattr("epicevents.auth.current_user.load_token", lambda: "token")
    monkeypatch.setattr("epicevents.auth.current_user.decode_token", lambda token: {"user_id": 1})
    monkeypatch.setattr("epicevents.auth.current_user.SessionLocal", lambda: session)

    result = get_current_user()

    assert result.id == 1
    assert result.role.name == "MANAGEMENT"
    assert session.closed is True