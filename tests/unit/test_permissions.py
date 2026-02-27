import pytest

from epicevents.security.permissions import (
    has_permission,
    require_permission,
    READ_ALL,
    COLLAB_CREATE,
    EVENT_CREATE,
    EVENT_UPDATE_ASSIGNED,
)


def test_unknown_role_has_no_permissions():
    assert has_permission("UNKNOWN", READ_ALL) is False


def test_management_can_create_collaborator():
    assert has_permission("MANAGEMENT", COLLAB_CREATE) is True


def test_sales_can_create_event_if_defined():
    assert has_permission("SALES", EVENT_CREATE) is True


def test_support_can_update_assigned_event():
    assert has_permission("SUPPORT", EVENT_UPDATE_ASSIGNED) is True


def test_support_cannot_create_collaborator():
    assert has_permission("SUPPORT", COLLAB_CREATE) is False


def test_require_permission_raises_when_denied():
    with pytest.raises(PermissionError):
        require_permission("SUPPORT", COLLAB_CREATE)