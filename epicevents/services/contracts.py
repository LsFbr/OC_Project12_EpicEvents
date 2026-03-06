from sqlalchemy import select
from sqlalchemy.orm import Session

from epicevents.models.contract import Contract
from epicevents.auth.utils import require_authentication
from epicevents.security.permissions import READ_ALL, require_permission
from epicevents.auth.current_user import get_current_user

def get_all_contracts(session: Session) -> list[Contract]:
    
    require_authentication()

    user = get_current_user()
    require_permission(user.role.name, READ_ALL)

    result = session.execute(select(Contract))
    return result.scalars().all()