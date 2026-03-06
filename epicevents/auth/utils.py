from epicevents.auth.token_storage import load_token
from epicevents.auth.jwt import decode_token


def require_authentication() -> None:
    token = load_token()

    if token is None:
        raise Exception("You must login first")

    decode_token(token)