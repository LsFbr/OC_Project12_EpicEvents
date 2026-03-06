from epicevents.auth.token_storage import delete_token

def logout() -> None:
    if not delete_token():
        raise Exception("You were not logged in")