import pytest

from epicevents.auth.current_user import get_current_user


class FakeUser:
    def __init__(self, user_id):
        self.id = user_id

class FakeQuery:
    def __init__(self, user):
        self.user = user

    def filter_by(self, **kwargs):
        return self

    def first(self):
        return self.user


class FakeSession:
    def __init__(self, user):
        self.user = user

    def query(self, model):
        return FakeQuery(self.user)

    def close(self):
        pass


def raise_invalid_token():
    raise Exception("Invalid token")


def test_get_current_user_no_token(monkeypatch):

    monkeypatch.setattr("epicevents.auth.current_user.load_token", lambda: None)

    with pytest.raises(Exception):
        get_current_user()


def test_get_current_user_invalid_token(monkeypatch):

    monkeypatch.setattr("epicevents.auth.current_user.load_token", lambda: "fake-token")

    monkeypatch.setattr("epicevents.auth.current_user.decode_token", raise_invalid_token)

    with pytest.raises(Exception):
        get_current_user()


def test_get_current_user_user_deleted(monkeypatch):

    monkeypatch.setattr("epicevents.auth.current_user.load_token", lambda: "token")

    monkeypatch.setattr("epicevents.auth.current_user.decode_token", lambda token: {"user_id": 1})

    monkeypatch.setattr("epicevents.auth.current_user.SessionLocal", lambda: FakeSession(None))

    with pytest.raises(Exception):
        get_current_user()


def test_get_current_user_success(monkeypatch):


    monkeypatch.setattr("epicevents.auth.current_user.load_token", lambda: "token")

    monkeypatch.setattr("epicevents.auth.current_user.decode_token", lambda token: {"user_id": 1})


    monkeypatch.setattr("epicevents.auth.current_user.SessionLocal", lambda: FakeSession(FakeUser(1)))

    result = get_current_user()

    assert result.id == 1