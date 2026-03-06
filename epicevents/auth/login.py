from epicevents.models.collaborator import Collaborator
from epicevents.db.session import SessionLocal
from epicevents.security.passwords import verify_password

from epicevents.auth.jwt import generate_token
from epicevents.auth.token_storage import save_token


def login(email: str, password: str) -> str:

    session = SessionLocal()

    try:
        user = session.query(Collaborator).filter_by(email=email).first()

        if user is None:
            raise Exception("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise Exception("Invalid email or password")

        token = generate_token(user)

        save_token(token)

        return token
    
    finally:
        session.close()