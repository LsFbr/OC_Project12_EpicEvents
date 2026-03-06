from sqlalchemy import select
from sqlalchemy.orm import Session

from epicevents.models.event import Event
from epicevents.auth.utils import require_authentication
from epicevents.security.permissions import READ_ALL, require_permission
from epicevents.auth.current_user import get_current_user

def get_all_events(session: Session) -> list[Event]:
    
    require_authentication()

    user = get_current_user()
    require_permission(user.role.name, READ_ALL)

    result = session.execute(select(Event))
    return result.scalars().all()