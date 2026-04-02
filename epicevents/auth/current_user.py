from sqlalchemy.orm import joinedload

from epicevents.auth.token_storage import load_token
from epicevents.auth.jwt import decode_token
from epicevents.db.session import SessionLocal
from epicevents.models.collaborator import Collaborator
from epicevents.exceptions import NotLoggedInError, UserNotFoundError


def get_current_user() -> Collaborator:
    token = load_token()

    if token is None:
        raise NotLoggedInError("You are not logged in")

    payload = decode_token(token)

    session = SessionLocal()

    try:
        # Load the collaborator with the role
        user = (
            session.query(Collaborator)
            .options(joinedload(Collaborator.role))
            .filter_by(id=payload["user_id"])
            .first()
        )

        if user is None:
            raise UserNotFoundError("User no longer exists")

        return user
    finally:
        session.close()
