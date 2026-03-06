import pytest
from pathlib import Path

from epicevents.auth.token_storage import get_token_path, save_token, load_token, delete_token


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """
    Replace Path.home() with a temporary directory.
    """
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path

def test_get_token_path_returns_correct_path(fake_home):
    token_path = get_token_path()
    assert token_path == fake_home / ".epicevents" / "token"


def test_save_token_creates_file(fake_home):
    token = "abc123"

    token_path = save_token(token)

    assert token_path.exists()
    assert token_path.read_text() == token


def test_load_token_returns_token(fake_home):
    token = "abc123"

    save_token(token)

    loaded = load_token()

    assert loaded == token


def test_load_token_returns_none_when_missing(fake_home):
    token = load_token()

    assert token is None


def test_delete_token_removes_file(fake_home):
    save_token("abc123")

    deleted = delete_token()

    assert deleted is True
    assert load_token() is None


def test_delete_token_when_missing(fake_home):
    deleted = delete_token()

    assert deleted is False


def test_save_token_creates_directory(fake_home):
    token = "abc123"

    token_path = save_token(token)

    assert token_path.parent.exists()