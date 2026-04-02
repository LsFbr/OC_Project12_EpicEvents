import pytest

from epicevents.security.permissions import (
    has_permission,
    require_permission,
    READ_ALL,
    COLLAB_CREATE,
    EVENT_CREATE,
    EVENT_UPDATE_ASSIGNED,
)
from epicevents.exceptions import BusinessAuthorizationError


# -------------------------
# has_permission
# -------------------------

def test_has_permission_returns_false_for_unknown_role():
    assert has_permission("UNKNOWN", READ_ALL) is False


def test_has_permission_returns_true_for_known_allowed_permission():
    assert has_permission("MANAGEMENT", COLLAB_CREATE) is True


def test_has_permission_returns_false_for_known_denied_permission():
    assert has_permission("SUPPORT", COLLAB_CREATE) is False


def test_has_permission_returns_true_for_another_valid_case():
    assert has_permission("SALES", EVENT_CREATE) is True


def test_has_permission_returns_true_for_support_valid_case():
    assert has_permission("SUPPORT", EVENT_UPDATE_ASSIGNED) is True


# -------------------------
# require_permission
# -------------------------

def test_require_permission_does_not_raise_when_has_permission_is_true(monkeypatch):
    called = {}

    def fake_has_permission(role_name, action):
        called["role_name"] = role_name
        called["action"] = action
        return True

    monkeypatch.setattr("epicevents.security.permissions.has_permission", fake_has_permission)

    require_permission("SALES", EVENT_CREATE)

    assert called == {
        "role_name": "SALES",
        "action": EVENT_CREATE,
    }


def test_require_permission_raises_when_has_permission_is_false(monkeypatch):
    called = {}

    def fake_has_permission(role_name, action):
        called["role_name"] = role_name
        called["action"] = action
        return False

    monkeypatch.setattr("epicevents.security.permissions.has_permission", fake_has_permission)

    with pytest.raises(BusinessAuthorizationError, match="Permission denied"):
        require_permission("SUPPORT", COLLAB_CREATE)

    assert called == {
        "role_name": "SUPPORT",
        "action": COLLAB_CREATE,
    }


def test_require_permission_error_message_contains_role_and_action(monkeypatch):
    monkeypatch.setattr(
        "epicevents.security.permissions.has_permission",
        lambda role_name, action: False,
    )

    with pytest.raises(BusinessAuthorizationError) as exc_info:
        require_permission("SUPPORT", COLLAB_CREATE)

    message = str(exc_info.value)

    assert "SUPPORT" in message
    assert COLLAB_CREATE in message
