import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from typing import Any
from datetime import datetime, timedelta, timezone
import os

from epicevents.models.collaborator import Collaborator
from epicevents.constants import JWT_ALGORITHM, JWT_TOKEN_EXPIRATION_HOURS

SECRET_KEY = os.getenv("EPICEVENTS_SECRET")

if SECRET_KEY is None:
    raise RuntimeError("EPICEVENTS_SECRET environment variable not set")

def generate_token(user: Collaborator) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "user_id": user.id,
        "iat": now,
        "exp": now + timedelta(hours=JWT_TOKEN_EXPIRATION_HOURS),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

    return token


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload

    except ExpiredSignatureError:
        raise Exception("Authentication token has expired. Please login again.")

    except InvalidTokenError:
        raise Exception("Invalid authentication token.")