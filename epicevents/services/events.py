from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Any

from epicevents.models.collaborator import Collaborator
from epicevents.models.contract import Contract
from epicevents.models.event import Event
from epicevents.auth.utils import require_authentication
from epicevents.security.permissions import (
    READ_ALL,
    EVENT_CREATE,
    EVENT_UPDATE_ASSIGNED,
    EVENT_ASSIGN_SUPPORT,
    EVENT_FILTER_BY_SUPPORT_CONTACT_ID,
    EVENT_FILTER_BY_MINE,
    require_permission,
    has_permission,
)
from epicevents.auth.current_user import get_current_user
from epicevents.exceptions import BusinessValidationError, BusinessAuthorizationError


def _require_datetime(value: Any, field_name: str) -> datetime:
    if value is None:
        raise BusinessValidationError(f"{field_name} is required")
    if not isinstance(value, datetime):
        raise BusinessValidationError(f"{field_name} must be a datetime")
    return value


def _require_support_collaborator(session: Session, support_contact_id: int) -> Collaborator:
    if not support_contact_id:
        raise BusinessValidationError("support_contact_id is required")

    collaborator = (
        session.query(Collaborator)
        .filter(Collaborator.id == support_contact_id)
        .one_or_none()
    )
    if collaborator is None:
        raise BusinessValidationError("support collaborator not found")

    if collaborator.role.name != "SUPPORT":
        raise BusinessValidationError("collaborator is not support")

    return collaborator


def get_all_events(
    session: Session,
    support_contact_id: int | None = None,
    assigned_to_me: bool = False,
) -> list[Event]:
    require_authentication()

    user = get_current_user()
    require_permission(user.role.name, READ_ALL)

    if support_contact_id is not None and assigned_to_me:
        raise BusinessValidationError("support_contact_id and assigned_to_me cannot be used together")

    if support_contact_id is not None and not has_permission(user.role.name, EVENT_FILTER_BY_SUPPORT_CONTACT_ID):
        raise BusinessAuthorizationError("only management can filter by support_contact_id")

    if assigned_to_me and not has_permission(user.role.name, EVENT_FILTER_BY_MINE):
        raise BusinessAuthorizationError("only support can use the mine filter")

    statement = select(Event)

    if support_contact_id is not None:
        statement = statement.where(Event.support_contact_id == support_contact_id)

    if assigned_to_me:
        statement = statement.where(Event.support_contact_id == user.id)

    result = session.execute(statement)
    return result.scalars().all()


def create_event(
    session: Session,
    title: str,
    notes: str,
    location: str,
    attendees: int,
    date_start: datetime,
    date_end: datetime,
    contract_id: int,
) -> Event:
    title = (title or "").strip()
    notes = (notes or "").strip()
    location = (location or "").strip()

    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, EVENT_CREATE)

    if not title:
        raise BusinessValidationError("title is required")
    if not location:
        raise BusinessValidationError("location is required")
    if attendees is None:
        raise BusinessValidationError("attendees is required")
    if not isinstance(attendees, int):
        raise BusinessValidationError("attendees must be an integer")
    if attendees < 0:
        raise BusinessValidationError("attendees must be greater than or equal to 0")

    date_start = _require_datetime(date_start, "date_start")
    date_end = _require_datetime(date_end, "date_end")

    if date_end < date_start:
        raise BusinessValidationError("date_end must be greater than or equal to date_start")

    if not contract_id:
        raise BusinessValidationError("contract_id is required")

    contract = session.query(Contract).filter(Contract.id == contract_id).one_or_none()
    if contract is None:
        raise BusinessValidationError("contract not found")

    if not contract.is_signed:
        raise BusinessValidationError("contract must be signed")

    if contract.client.sales_contact_id != user.id:
        raise BusinessAuthorizationError("you are not the sales contact of this contract")

    event = Event(
        title=title,
        notes=notes,
        location=location,
        attendees=attendees,
        date_start=date_start,
        date_end=date_end,
        support_contact_id=None,
        contract_id=contract.id,
    )

    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def update_event(
    session: Session,
    event_id: int,
    **fields: Any,
) -> Event:
    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, EVENT_UPDATE_ASSIGNED)


    if event_id is None:
        raise BusinessValidationError("event id is required")
    if not fields:
        raise BusinessValidationError("no fields to update")

    event = session.query(Event).filter(Event.id == event_id).one_or_none()
    if event is None:
        raise BusinessValidationError("event not found")


    if event.support_contact_id != user.id:
        raise BusinessAuthorizationError("you are not the support contact of this event")

    allowed_fields = {"title", "notes", "location", "attendees", "date_start", "date_end"}

    for field_name in fields:
        if field_name not in allowed_fields:
            raise BusinessValidationError(f"forbidden field: {field_name}")

    if "title" in fields:
        title = (fields["title"] or "").strip()
        if not title:
            raise BusinessValidationError("title is required")
        event.title = title

    if "notes" in fields:
        event.notes = (fields["notes"] or "").strip()

    if "location" in fields:
        location = (fields["location"] or "").strip()
        if not location:
            raise BusinessValidationError("location is required")
        event.location = location

    if "attendees" in fields:
        attendees = fields["attendees"]
        if attendees is None:
            raise BusinessValidationError("attendees is required")
        if not isinstance(attendees, int):
            raise BusinessValidationError("attendees must be an integer")
        if attendees < 0:
            raise BusinessValidationError("attendees must be greater than or equal to 0")
        event.attendees = attendees

    new_date_start = event.date_start
    new_date_end = event.date_end

    if "date_start" in fields:
        new_date_start = _require_datetime(fields["date_start"], "date_start")

    if "date_end" in fields:
        new_date_end = _require_datetime(fields["date_end"], "date_end")

    if new_date_end < new_date_start:
        raise BusinessValidationError("date_end must be greater than or equal to date_start")

    event.date_start = new_date_start
    event.date_end = new_date_end

    session.commit()
    session.refresh(event)
    return event


def assign_support(
    session: Session,
    event_id: int,
    support_contact_id: int | None,
) -> Event:
    require_authentication()
    user = get_current_user()
    require_permission(user.role.name, EVENT_ASSIGN_SUPPORT)

    if event_id is None:
        raise BusinessValidationError("event_id is required")

    event = session.query(Event).filter(Event.id == event_id).one_or_none()
    if event is None:
        raise BusinessValidationError("event not found")

    if support_contact_id is None:
        return event

    collaborator = _require_support_collaborator(session, support_contact_id)
    event.support_contact_id = collaborator.id

    session.commit()
    session.refresh(event)
    return event