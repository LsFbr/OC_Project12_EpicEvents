import pytest
from epicevents.auth.logout import logout
from epicevents.exceptions import NotLoggedInError

def test_logout_success(monkeypatch):
    monkeypatch.setattr("epicevents.auth.logout.delete_token", lambda: True)
    logout()
    

def test_logout_not_logged_in(monkeypatch):
    monkeypatch.setattr("epicevents.auth.logout.delete_token", lambda: False)
    with pytest.raises(NotLoggedInError):
        logout()
