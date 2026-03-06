import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from typing import Any
from datetime import datetime, timedelta, timezone
import os

from epicevents.models.collaborator import Collaborator

SECRET_KEY = os.getenv("EPICEVENTS_SECRET")

if SECRET_KEY is None:
    raise RuntimeError("EPICEVENTS_SECRET environment variable not set")

ALGORITHM = "HS256"
TOKEN_EXPIRATION_HOURS = 8


def generate_token(user: Collaborator) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "user_id": user.id,
        "iat": now,
        "exp": now + timedelta(hours=TOKEN_EXPIRATION_HOURS),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except ExpiredSignatureError:
        raise Exception("Authentication token has expired. Please login again.")

    except InvalidTokenError:
        raise Exception("Invalid authentication token.")