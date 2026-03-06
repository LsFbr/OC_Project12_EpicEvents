import pytest

from epicevents.auth.login import login





def test_login_user_not_found(monkeypatch, fake_session):

    monkeypatch.setattr("epicevents.auth.login.SessionLocal", lambda: fake_session)

    with pytest.raises(Exception):
        login("test@test.com", "password")


def test_login_wrong_password(monkeypatch, fake_session):

    monkeypatch.setattr("epicevents.auth.login.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.auth.login.verify_password", lambda password, hash: False)

    with pytest.raises(Exception):
        login("test@test.com", "password")


def test_login_success(monkeypatch, fake_session):

    monkeypatch.setattr("epicevents.auth.login.SessionLocal", lambda: fake_session)
    monkeypatch.setattr("epicevents.auth.login.verify_password", lambda password, hash: True)
    monkeypatch.setattr("epicevents.auth.login.generate_token", lambda user: "fake-token")

    saved = {}

    def fake_save_token(token):
        saved["token"] = token

    monkeypatch.setattr("epicevents.auth.login.save_token", fake_save_token)

    token = login("test@test.com", "password")

    assert token == "fake-token"
    assert saved["token"] == "fake-token"