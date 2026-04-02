import pytest
from datetime import datetime, timedelta

from tests.conftest import FakeClient, FakeContract, FakeEvent, FakeSession
from epicevents.security.permissions import EVENT_FILTER_BY_SUPPORT_CONTACT_ID, EVENT_FILTER_BY_MINE
from epicevents.models.collaborator import Collaborator
from epicevents.models.contract import Contract
from epicevents.models.event import Event
from epicevents.services.events import (
    _require_datetime,
    _require_support_collaborator,
    get_all_events,
    create_event,
    update_event,
    assign_support,
)
from epicevents.exceptions import (
    NotLoggedInError,
    UserNotFoundError,
    BusinessAuthorizationError,
    BusinessValidationError,
)


def raise_authentication_failed():
    raise NotLoggedInError("Authentication failed")


def raise_no_user():
    raise UserNotFoundError("User no longer exists")


def raise_no_permission(role_name, action):
    raise BusinessAuthorizationError("No permission")


def allow_authenticated_user(monkeypatch, user):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)


@pytest.fixture
def base_dates():
    start = datetime(2026, 6, 1, 9, 0)
    end = start + timedelta(hours=2)
    return start, end


@pytest.fixture
def owned_client(sales_user):
    return FakeClient(client_id=1, sales_contact_id=sales_user.id)


@pytest.fixture
def unowned_client():
    return FakeClient(client_id=2, sales_contact_id=999)


@pytest.fixture
def signed_owned_contract(owned_client):
    return FakeContract(contract_id=1, client=owned_client, is_signed=True)


@pytest.fixture
def unsigned_owned_contract(owned_client):
    return FakeContract(contract_id=2, client=owned_client, is_signed=False)


@pytest.fixture
def signed_unowned_contract(unowned_client):
    return FakeContract(contract_id=3, client=unowned_client, is_signed=True)


@pytest.fixture
def event_assigned_to_support(support_user, base_dates):
    start, end = base_dates
    return FakeEvent(
        event_id=1,
        title="Event One",
        notes="Notes One",
        location="Paris",
        attendees=10,
        date_start=start,
        date_end=end,
        contract_id=1,
        support_contact_id=support_user.id,
    )


@pytest.fixture
def event_without_support(base_dates):
    start, end = base_dates
    return FakeEvent(
        event_id=2,
        title="Event Two",
        notes="Notes Two",
        location="Lyon",
        attendees=20,
        date_start=start,
        date_end=end,
        contract_id=1,
        support_contact_id=None,
    )


@pytest.fixture
def event_assigned_to_other_support(base_dates):
    start, end = base_dates
    return FakeEvent(
        event_id=3,
        title="Event Three",
        notes="Notes Three",
        location="Marseille",
        attendees=30,
        date_start=start,
        date_end=end,
        contract_id=3,
        support_contact_id=999,
    )


# -------------------------
# _require_datetime
# -------------------------

def test_require_datetime_ok(base_dates):
    start, end = base_dates
    assert _require_datetime(start, "date_start") == start


def test_require_datetime_rejects_none():
    with pytest.raises(BusinessValidationError, match="date_start is required"):
        _require_datetime(None, "date_start")


def test_require_datetime_rejects_invalid_type():
    with pytest.raises(BusinessValidationError, match="date_start must be a datetime"):
        _require_datetime("2026-01-01", "date_start")


# -------------------------
# _require_support_collaborator
# -------------------------

def test_require_support_collaborator_ok(support_user):
    session = FakeSession(query_map={Collaborator: [support_user]})

    collaborator = _require_support_collaborator(session, support_user.id)

    assert collaborator == support_user


def test_require_support_collaborator_rejects_missing_id():
    session = FakeSession(query_map={Collaborator: []})

    with pytest.raises(BusinessValidationError, match="support_contact_id is required"):
        _require_support_collaborator(session, None)


def test_require_support_collaborator_rejects_not_found():
    session = FakeSession(query_map={Collaborator: []})

    with pytest.raises(BusinessValidationError, match="support collaborator not found"):
        _require_support_collaborator(session, 999)


def test_require_support_collaborator_rejects_non_support(sales_user):
    session = FakeSession(query_map={Collaborator: [sales_user]})

    with pytest.raises(BusinessValidationError, match="collaborator is not support"):
        _require_support_collaborator(session, sales_user.id)


# -------------------------
# get_all_events
# -------------------------

def test_get_all_events_ok(monkeypatch, fake_user, event_assigned_to_support, event_without_support):
    session = FakeSession(execute_items=[event_assigned_to_support, event_without_support])

    allow_authenticated_user(monkeypatch, fake_user)

    events = get_all_events(session)

    assert len(events) == 2
    assert events[0] == event_assigned_to_support
    assert events[1] == event_without_support


def test_get_all_events_rejects_combined_filters(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="support_contact_id and assigned_to_me cannot be used together"):
        get_all_events(session, support_contact_id=20, assigned_to_me=True)


def test_get_all_events_filter_by_support_contact_id_ok(monkeypatch, fake_user, event_assigned_to_support):
    session = FakeSession(execute_items=[event_assigned_to_support])

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr(
        "epicevents.services.events.has_permission",
        lambda role, action: action == EVENT_FILTER_BY_SUPPORT_CONTACT_ID,
    )

    events = get_all_events(session, support_contact_id=event_assigned_to_support.support_contact_id)

    assert len(events) == 1
    assert events[0] == event_assigned_to_support
    assert events[0].support_contact_id == event_assigned_to_support.support_contact_id


def test_get_all_events_filter_by_support_contact_id_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)
    monkeypatch.setattr("epicevents.services.events.has_permission", lambda role, action: False)

    with pytest.raises(BusinessAuthorizationError, match="only management can filter by support_contact_id"):
        get_all_events(session, support_contact_id=20)


def test_get_all_events_filter_by_mine_ok(monkeypatch, support_user, event_assigned_to_support):
    session = FakeSession(execute_items=[event_assigned_to_support])

    allow_authenticated_user(monkeypatch, support_user)
    monkeypatch.setattr(
        "epicevents.services.events.has_permission",
        lambda role, action: action == EVENT_FILTER_BY_MINE,
    )

    events = get_all_events(session, assigned_to_me=True)

    assert len(events) == 1
    assert events[0] == event_assigned_to_support
    assert events[0].support_contact_id == support_user.id


def test_get_all_events_filter_by_mine_no_permission(monkeypatch, support_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, support_user)
    monkeypatch.setattr("epicevents.services.events.has_permission", lambda role, action: False)

    with pytest.raises(BusinessAuthorizationError, match="only support can use the mine filter"):
        get_all_events(session, assigned_to_me=True)


# -------------------------
# create_event
# -------------------------

def test_create_event_ok(monkeypatch, sales_user, signed_owned_contract, base_dates):
    session = FakeSession(query_map={Contract: [signed_owned_contract]})
    start, end = base_dates

    allow_authenticated_user(monkeypatch, sales_user)

    monkeypatch.setattr("epicevents.services.events._require_datetime", lambda value, field_name: value)

    event = create_event(
        session=session,
        title="  New Event  ",
        notes="  Some notes  ",
        location="  Paris  ",
        attendees=50,
        date_start=start,
        date_end=end,
        contract_id=1,
    )

    assert event.title == "New Event"
    assert event.notes == "Some notes"
    assert event.location == "Paris"
    assert event.support_contact_id is None
    assert session.committed is True


def test_create_event_no_permission(monkeypatch, fake_user, base_dates):
    session = FakeSession()
    start, end = base_dates

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", raise_no_permission)

    with pytest.raises(BusinessAuthorizationError, match="No permission"):
        create_event(session, "A", "B", "Paris", 10, start, end, 1)


def test_create_event_rejects_missing_title(monkeypatch, fake_user, base_dates):
    session = FakeSession()
    start, end = base_dates

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="title is required"):
        create_event(session, "", "B", "Paris", 10, start, end, 1)


def test_create_event_rejects_missing_location(monkeypatch, fake_user, base_dates):
    session = FakeSession()
    start, end = base_dates

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="location is required"):
        create_event(session, "A", "B", "", 10, start, end, 1)


def test_create_event_rejects_invalid_attendees(monkeypatch, fake_user, base_dates):
    session = FakeSession()
    start, end = base_dates

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="attendees must be an integer"):
        create_event(session, "A", "B", "Paris", "10", start, end, 1)


def test_create_event_rejects_negative_attendees(monkeypatch, fake_user, base_dates):
    session = FakeSession()
    start, end = base_dates

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="attendees must be greater than or equal to 0"):
        create_event(session, "A", "B", "Paris", -1, start, end, 1)


def test_create_event_rejects_date_order(monkeypatch, fake_user, base_dates):
    session = FakeSession()
    start, _ = base_dates
    end = start - timedelta(hours=1)

    allow_authenticated_user(monkeypatch, fake_user)

    monkeypatch.setattr("epicevents.services.events._require_datetime", lambda value, field_name: value)

    with pytest.raises(BusinessValidationError, match="date_end must be greater than or equal to date_start"):
        create_event(session, "A", "B", "Paris", 10, start, end, 1)


def test_create_event_rejects_contract_not_found(monkeypatch, fake_user, base_dates):
    session = FakeSession(query_map={Contract: []})
    start, end = base_dates

    allow_authenticated_user(monkeypatch, fake_user)

    monkeypatch.setattr("epicevents.services.events._require_datetime", lambda value, field_name: value)

    with pytest.raises(BusinessValidationError, match="contract not found"):
        create_event(session, "A", "B", "Paris", 10, start, end, 999)


def test_create_event_rejects_unsigned_contract(monkeypatch, fake_user, unsigned_owned_contract, base_dates):
    session = FakeSession(query_map={Contract: [unsigned_owned_contract]})
    start, end = base_dates

    allow_authenticated_user(monkeypatch, fake_user)

    monkeypatch.setattr("epicevents.services.events._require_datetime", lambda value, field_name: value)

    with pytest.raises(BusinessValidationError, match="contract must be signed"):
        create_event(session, "A", "B", "Paris", 10, start, end, 2)


def test_create_event_rejects_unowned_contract(monkeypatch, sales_user, signed_unowned_contract, base_dates):
    session = FakeSession(query_map={Contract: [signed_unowned_contract]})
    start, end = base_dates

    allow_authenticated_user(monkeypatch, sales_user)

    monkeypatch.setattr("epicevents.services.events._require_datetime", lambda value, field_name: value)

    with pytest.raises(BusinessAuthorizationError, match="you are not the sales contact of this contract"):
        create_event(session, "A", "B", "Paris", 10, start, end, 3)


# -------------------------
# update_event
# -------------------------

def test_update_event_ok(monkeypatch, support_user, event_assigned_to_support):
    session = FakeSession(query_map={Event: [event_assigned_to_support]})
    start = datetime(2026, 7, 1, 10, 0)
    end = start + timedelta(hours=3)

    allow_authenticated_user(monkeypatch, support_user)

    monkeypatch.setattr("epicevents.services.events._require_datetime", lambda value, field_name: value)

    event = update_event(
        session=session,
        event_id=1,
        title="Updated Event",
        notes="Updated Notes",
        location="Updated Location",
        attendees=99,
        date_start=start,
        date_end=end,
    )

    assert event.title == "Updated Event"
    assert event.attendees == 99
    assert session.committed is True


def test_update_event_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", raise_no_permission)

    with pytest.raises(BusinessAuthorizationError, match="No permission"):
        update_event(session, 1, title="Updated")


def test_update_event_rejects_no_fields(monkeypatch, fake_user):
    session = FakeSession()

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="no fields to update"):
        update_event(session, 1)


def test_update_event_rejects_event_not_found(monkeypatch, fake_user):
    session = FakeSession(query_map={Event: []})

    allow_authenticated_user(monkeypatch, fake_user)

    with pytest.raises(BusinessValidationError, match="event not found"):
        update_event(session, 999, title="Updated")


def test_update_event_rejects_support_not_assigned(monkeypatch, support_user, event_without_support):
    session = FakeSession(query_map={Event: [event_without_support]})

    allow_authenticated_user(monkeypatch, support_user)

    with pytest.raises(BusinessAuthorizationError, match="you are not the support contact of this event"):
        update_event(session, 2, title="Updated")


def test_update_event_rejects_forbidden_field(monkeypatch, support_user, event_assigned_to_support):
    session = FakeSession(query_map={Event: [event_assigned_to_support]})

    allow_authenticated_user(monkeypatch, support_user)

    with pytest.raises(BusinessValidationError, match="forbidden field: support_contact_id"):
        update_event(session, 1, support_contact_id=20)


def test_update_event_rejects_invalid_attendees(monkeypatch, support_user, event_assigned_to_support):
    session = FakeSession(query_map={Event: [event_assigned_to_support]})

    allow_authenticated_user(monkeypatch, support_user)

    with pytest.raises(BusinessValidationError, match="attendees must be an integer"):
        update_event(session, 1, attendees="99")


def test_update_event_rejects_date_order(monkeypatch, support_user, event_assigned_to_support):
    session = FakeSession(query_map={Event: [event_assigned_to_support]})
    start = datetime(2026, 7, 1, 10, 0)
    end = start - timedelta(hours=1)

    allow_authenticated_user(monkeypatch, support_user)

    monkeypatch.setattr("epicevents.services.events._require_datetime", lambda value, field_name: value)

    with pytest.raises(BusinessValidationError, match="date_end must be greater than or equal to date_start"):
        update_event(session, 1, date_start=start, date_end=end)


# -------------------------
# assign_support
# -------------------------

def test_assign_support_ok(monkeypatch, management_user, event_without_support, support_user):
    session = FakeSession(query_map={Event: [event_without_support]})

    allow_authenticated_user(monkeypatch, management_user)

    monkeypatch.setattr(
        "epicevents.services.events._require_support_collaborator",
        lambda session, support_contact_id: support_user,
    )

    event = assign_support(session, 2, support_user.id)

    assert event.support_contact_id == support_user.id
    assert session.committed is True


def test_assign_support_no_permission(monkeypatch, fake_user):
    session = FakeSession()

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", raise_no_permission)

    with pytest.raises(BusinessAuthorizationError, match="No permission"):
        assign_support(session, 1, 20)


def test_assign_support_rejects_event_not_found(monkeypatch, fake_user):
    session = FakeSession(query_map={Event: []})

    allow_authenticated_user(monkeypatch, fake_user)

    monkeypatch.setattr(
        "epicevents.services.events._require_support_collaborator",
        lambda session, support_contact_id: fake_user,
    )

    with pytest.raises(BusinessValidationError, match="event not found"):
        assign_support(session, 999, 20)


def test_assign_support_rejects_non_support(monkeypatch, management_user, event_without_support, sales_user):
    session = FakeSession(query_map={Event: [event_without_support]})

    def raise_not_support(session, support_contact_id):
        raise BusinessValidationError("collaborator is not support")

    allow_authenticated_user(monkeypatch, management_user)

    monkeypatch.setattr("epicevents.services.events._require_support_collaborator", raise_not_support)

    with pytest.raises(BusinessValidationError, match="collaborator is not support"):
        assign_support(session, 2, sales_user.id)
