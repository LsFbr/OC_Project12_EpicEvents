from epicevents.auth.token_storage import load_token
from epicevents.auth.jwt import decode_token
from epicevents.exceptions import NotLoggedInError


def require_authentication() -> None:
    token = load_token()

    if token is None:
        raise NotLoggedInError("You must login first")

    decode_token(token)
