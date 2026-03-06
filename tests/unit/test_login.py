import pytest

from epicevents.auth.login import login


class FakeUser:
    def __init__(self, email="test@test.com", password_hash="hashed", user_id=1):
        self.email = email
        self.password_hash = password_hash
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


def test_login_user_not_found(monkeypatch):

    monkeypatch.setattr("epicevents.auth.login.SessionLocal", lambda: FakeSession(None))

    with pytest.raises(Exception):
        login("test@test.com", "password")


def test_login_wrong_password(monkeypatch):

    user = FakeUser()

    monkeypatch.setattr("epicevents.auth.login.SessionLocal", lambda: FakeSession(user))
    monkeypatch.setattr("epicevents.auth.login.verify_password", lambda password, hash: False)

    with pytest.raises(Exception):
        login("test@test.com", "password")


def test_login_success(monkeypatch):

    user = FakeUser()

    monkeypatch.setattr("epicevents.auth.login.SessionLocal", lambda: FakeSession(user))
    monkeypatch.setattr("epicevents.auth.login.verify_password", lambda password, hash: True)
    monkeypatch.setattr("epicevents.auth.login.generate_token", lambda user: "fake-token")

    saved = {}

    def fake_save_token(token):
        saved["token"] = token

    monkeypatch.setattr("epicevents.auth.login.save_token", fake_save_token)

    token = login("test@test.com", "password")

    assert token == "fake-token"
    assert saved["token"] == "fake-token"