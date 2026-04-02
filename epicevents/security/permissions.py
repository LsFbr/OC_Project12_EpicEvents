from typing import Set, Dict
from epicevents.exceptions import BusinessAuthorizationError
READ_ALL = "read all data"

COLLAB_CREATE = "create a collaborator"
COLLAB_UPDATE = "update a collaborator"
COLLAB_DELETE = "delete a collaborator"

CLIENT_CREATE = "create a client"
CLIENT_UPDATE_OWNED = "update a client you own"

CONTRACT_CREATE = "create a contract"
CONTRACT_UPDATE_ANY = "update a contract"
CONTRACT_UPDATE_OWNED = "update a contract you own"
CONTRACT_FILTER_BY_PAID_UNPAID = "filter by paid and unpaid contracts"
CONTRACT_FILTER_BY_SIGNED_NOT_SIGNED = "filter by signed and not signed contracts"

EVENT_CREATE = "create an event"
EVENT_UPDATE_ASSIGNED = "update an event"
EVENT_ASSIGN_SUPPORT = "assign support to an event"
EVENT_FILTER_BY_SUPPORT_CONTACT_ID = "filter by events assigned to a support contact"
EVENT_FILTER_BY_MINE = "filter by events assigned to me"

PERMISSIONS: Dict[str, Set[str]] = {
    "MANAGEMENT": {
        READ_ALL,
        COLLAB_CREATE, COLLAB_UPDATE, COLLAB_DELETE,
        CONTRACT_CREATE, CONTRACT_UPDATE_ANY,
        EVENT_ASSIGN_SUPPORT,
        EVENT_FILTER_BY_SUPPORT_CONTACT_ID,
    },
    "SALES": {
        READ_ALL,
        CLIENT_CREATE, CLIENT_UPDATE_OWNED,
        CONTRACT_UPDATE_OWNED,
        CONTRACT_FILTER_BY_PAID_UNPAID,
        CONTRACT_FILTER_BY_SIGNED_NOT_SIGNED,
        EVENT_CREATE,
    },
    "SUPPORT": {
        READ_ALL,
        EVENT_UPDATE_ASSIGNED,
        EVENT_FILTER_BY_MINE,
    },
}


def has_permission(role_name: str, action: str) -> bool:
    if role_name not in PERMISSIONS:
        return False
    return action in PERMISSIONS[role_name]


def require_permission(role_name: str, action: str) -> None:
    if not has_permission(role_name, action):
        raise BusinessAuthorizationError(
            f"Permission denied: your role ({role_name}) does not have the permission to {action}. "
            f"You need the {' or '.join([role for role in PERMISSIONS if action in PERMISSIONS[role]])} role(s) to perform this action."
        )
