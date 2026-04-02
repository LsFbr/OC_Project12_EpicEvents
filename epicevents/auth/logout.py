from epicevents.auth.token_storage import delete_token
from epicevents.exceptions import NotLoggedInError

def logout() -> None:
    """
    Logout a collaborator and delete the JWT token.
    Args:
        None
    Returns:
        None
    """
    if not delete_token():
        raise NotLoggedInError("You were not logged in")
