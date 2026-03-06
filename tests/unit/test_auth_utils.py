import pytest

from epicevents.auth.utils import require_authentication


def test_require_authentication_no_token(monkeypatch):

    monkeypatch.setattr("epicevents.auth.utils.load_token", lambda: None)

    with pytest.raises(Exception):
        require_authentication()


def test_require_authentication_with_token(monkeypatch):

    monkeypatch.setattr("epicevents.auth.utils.load_token", lambda: "fake-token")
    monkeypatch.setattr("epicevents.auth.utils.decode_token", lambda token: {"user_id": 1})

    require_authentication()
