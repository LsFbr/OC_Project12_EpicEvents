from epicevents.auth.token_storage import load_token
from epicevents.auth.jwt import decode_token
from epicevents.db.session import SessionLocal
from epicevents.models.collaborator import Collaborator


def get_current_user() -> Collaborator:
    token = load_token()

    if token is None:
        raise Exception("You are not logged in")

    payload = decode_token(token)

    session = SessionLocal()

    try:
        user = session.query(Collaborator).filter_by(id=payload["user_id"]).first()

        if user is None:
            raise Exception("User no longer exists")

        return user
    finally:
        session.close()