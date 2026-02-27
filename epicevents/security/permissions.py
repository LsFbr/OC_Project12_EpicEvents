from typing import Set, Dict

READ_ALL = "read:all"

COLLAB_CREATE = "collaborator:create"
COLLAB_UPDATE = "collaborator:update"
COLLAB_DELETE = "collaborator:delete"

CLIENT_CREATE = "client:create"
CLIENT_UPDATE_ANY = "client:update:any"
CLIENT_UPDATE_OWNED = "client:update:owned"

CONTRACT_CREATE = "contract:create"
CONTRACT_UPDATE_ANY = "contract:update:any"
CONTRACT_UPDATE_OWNED = "contract:update:owned"

EVENT_CREATE = "event:create"
EVENT_UPDATE_ANY = "event:update:any"
EVENT_UPDATE_ASSIGNED = "event:update:assigned"
EVENT_ASSIGN_SUPPORT = "event:assign_support"

PERMISSIONS: Dict[str, Set[str]] = {
    "MANAGEMENT": {
        READ_ALL,
        COLLAB_CREATE, COLLAB_UPDATE, COLLAB_DELETE,
        CONTRACT_CREATE, CONTRACT_UPDATE_ANY,
        EVENT_ASSIGN_SUPPORT,
    },
    "SALES": {
        READ_ALL,
        CLIENT_CREATE, CLIENT_UPDATE_OWNED,
        CONTRACT_UPDATE_OWNED,
        EVENT_CREATE,
    },
    "SUPPORT": {
        READ_ALL,
        EVENT_UPDATE_ASSIGNED,
    },
}


def has_permission(role_name: str, action: str) -> bool:
    if role_name not in PERMISSIONS:
        return False
    return action in PERMISSIONS[role_name]


def require_permission(role_name: str, action: str) -> None:
    if not has_permission(role_name, action):
        raise PermissionError(f"Permission denied: role={role_name} action={action}")