import pytest
from datetime import datetime, timedelta

from conftest import FakeUser

from epicevents.services.events import get_all_events, create_event, update_event
from epicevents.models.event import Event
from epicevents.models.client import Client
from epicevents.models.contract import Contract
from epicevents.models.collaborator import Collaborator
from epicevents.models.role import Role


@pytest.fixture
def seeded_roles(session):
    session.add_all([
        Role(name="SALES"),
        Role(name="SUPPORT"),
        Role(name="MANAGEMENT"),
    ])
    session.commit()


@pytest.fixture
def seeded_collaborators(session, seeded_roles):
    session.add_all([
        Collaborator(employee_number="1", full_name="Sales One", email="sales1@example.com", role_id=1, password_hash="hashed"),
        Collaborator(employee_number="2", full_name="Support One", email="support1@example.com", role_id=2, password_hash="hashed"),
        Collaborator(employee_number="3", full_name="Management One", email="management1@example.com", role_id=3, password_hash="hashed"),
        Collaborator(employee_number="4", full_name="Sales Two", email="sales2@example.com", role_id=1, password_hash="hashed"),
    ])
    session.commit()


@pytest.fixture
def seeded_clients(session, seeded_collaborators):
    session.add_all([
        Client(name="Client 1", email="client1@example.com", phone_number="1234567890", company_name="Company 1", sales_contact_id=1),
        Client(name="Client 2", email="client2@example.com", phone_number="1234567891", company_name="Company 2", sales_contact_id=1),
        Client(name="Client 3", email="client3@example.com", phone_number="1234567892", company_name="Company 3", sales_contact_id=4),
    ])
    session.commit()


@pytest.fixture
def seeded_contracts(session, seeded_clients):
    session.add_all([
        Contract(total_amount=1000, rest_amount=1000, is_signed=True, client_id=1),
        Contract(total_amount=2000, rest_amount=1500, is_signed=False, client_id=2),
        Contract(total_amount=3000, rest_amount=3000, is_signed=True, client_id=3),
    ])
    session.commit()


@pytest.fixture
def seeded_events(session, seeded_contracts, seeded_collaborators):
    now = datetime.now()
    session.add_all([
        Event(title="Event 1", notes="Notes 1", location="Location 1", attendees=10, date_start=now, date_end=now + timedelta(hours=2), contract_id=1, support_contact_id=2),
        Event(title="Event 2", notes="Notes 2", location="Location 2", attendees=20, date_start=now, date_end=now + timedelta(hours=3), contract_id=1, support_contact_id=None),
        Event(title="Event 3", notes="Notes 3", location="Location 3", attendees=30, date_start=now, date_end=now + timedelta(hours=4), contract_id=3, support_contact_id=None),
    ])
    session.commit()


def raise_authentication_failed():
    raise Exception("Authentication failed")


def raise_no_user():
    raise Exception("User no longer exists")


def raise_no_permission(role, action):
    raise PermissionError("No permission")

sales_user = FakeUser(user_id=1, role_name="SALES")
support_user = FakeUser(user_id=2, role_name="SUPPORT")
management_user = FakeUser(user_id=3, role_name="MANAGEMENT")


# get_all_events tests
def test_get_all_events_ok(session, seeded_events, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    events = get_all_events(session)
    assert len(events) == 3
    assert events[0].title == "Event 1"
    assert events[1].title == "Event 2"
    assert events[2].title == "Event 3"


def test_get_all_events_authentication_failed(session, seeded_events, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.events.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        get_all_events(session)


def test_get_all_events_no_user(session, seeded_events, monkeypatch):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        get_all_events(session)


def test_get_all_events_no_permission(session, seeded_events, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", raise_no_permission)

    with pytest.raises(PermissionError, match="No permission"):
        get_all_events(session)


def test_get_all_events_no_events(session, monkeypatch, fake_user):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: fake_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    events = get_all_events(session)
    assert len(events) == 0


# create_event tests
def test_create_event_ok(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    event = create_event(
        session=session,
        title="New Event",
        notes="Some notes",
        location="Paris",
        attendees=50,
        date_start=start,
        date_end=end,
        contract_id=1,
    )

    assert event.id is not None
    assert event.title == "New Event"
    assert event.notes == "Some notes"
    assert event.location == "Paris"
    assert event.attendees == 50
    assert event.contract_id == 1
    assert event.support_contact_id is None


def test_create_event_authentication_failed(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=1,
        )


def test_create_event_no_user(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=1,
        )


def test_create_event_no_permission(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", raise_no_permission)

    with pytest.raises(Exception, match="No permission"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=1,
        )


def test_create_event_rejects_missing_title(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="title is required"):
        create_event(
            session=session,
            title="",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=1,
        )


def test_create_event_rejects_missing_location(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="location is required"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=1,
        )


def test_create_event_rejects_missing_attendees(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="attendees is required"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=None,
            date_start=start,
            date_end=end,
            contract_id=1,
        )


def test_create_event_rejects_invalid_attendees_type(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="attendees must be an integer"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees="50",
            date_start=start,
            date_end=end,
            contract_id=1,
        )


def test_create_event_rejects_negative_attendees(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="attendees must be greater than or equal to 0"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=-1,
            date_start=start,
            date_end=end,
            contract_id=1,
        )


def test_create_event_rejects_missing_date_start(session, seeded_contracts, monkeypatch):
    end = datetime.now() + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="date_start is required"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=None,
            date_end=end,
            contract_id=1,
        )


def test_create_event_rejects_invalid_date_start_type(session, seeded_contracts, monkeypatch):
    end = datetime.now() + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="date_start must be a datetime"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start="2025-01-01",
            date_end=end,
            contract_id=1,
        )


def test_create_event_rejects_missing_date_end(session, seeded_contracts, monkeypatch):
    start = datetime.now()

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="date_end is required"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=None,
            contract_id=1,
        )


def test_create_event_rejects_invalid_date_end_type(session, seeded_contracts, monkeypatch):
    start = datetime.now()

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="date_end must be a datetime"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end="2025-01-01",
            contract_id=1,
        )


def test_create_event_rejects_date_end_before_date_start(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start - timedelta(hours=1)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="date_end must be greater than or equal to date_start"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=1,
        )


def test_create_event_rejects_missing_contract_id(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="contract_id is required"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=0,
        )


def test_create_event_rejects_contract_not_found(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="contract not found"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=999,
        )


def test_create_event_rejects_unsigned_contract(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="contract must be signed"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=2,
        )


def test_create_event_rejects_unowned_contract(session, seeded_contracts, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=2)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(PermissionError, match="you are not the sales contact of this contract"):
        create_event(
            session=session,
            title="New Event",
            notes="Some notes",
            location="Paris",
            attendees=50,
            date_start=start,
            date_end=end,
            contract_id=3,
        )


# update_event tests
def test_update_event_ok(session, seeded_events, monkeypatch):
    start = datetime.now()
    end = start + timedelta(hours=5)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    event_updated = update_event(
        session=session,
        event_id=1,
        title="Updated Event",
        notes="Updated notes",
        location="Updated location",
        attendees=99,
        date_start=start,
        date_end=end,
    )

    assert event_updated.id == 1
    assert event_updated.title == "Updated Event"
    assert event_updated.notes == "Updated notes"
    assert event_updated.location == "Updated location"
    assert event_updated.attendees == 99
    assert event_updated.date_start == start
    assert event_updated.date_end == end


def test_update_event_authentication_failed(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="Authentication failed"):
        update_event(
            session=session,
            event_id=1,
        )


def test_update_event_no_user(session, seeded_events, monkeypatch):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", raise_no_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(Exception, match="User no longer exists"):
        update_event(
            session=session,
            event_id=1,
        )


def test_update_event_no_permission(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: sales_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", raise_no_permission)

    with pytest.raises(PermissionError, match="No permission"):
        update_event(
            session=session,
            event_id=1,
            title="Updated Event",
        )


def test_update_event_rejects_missing_event_id(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="event id is required"):
        update_event(
            session=session,
            event_id=None,
            title="Updated Event",
        )


def test_update_event_rejects_no_fields(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="no fields to update"):
        update_event(
            session=session,
            event_id=1,
        )


def test_update_event_rejects_event_not_found(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="event not found"):
        update_event(
            session=session,
            event_id=999,
            support_contact_id=2,
        )


def test_update_event_rejects_support_not_assigned_event(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(PermissionError, match="you are not the support contact of this event"):
        update_event(
            session=session,
            event_id=2,
            title="Updated Event",
        )


def test_update_event_rejects_forbidden_field(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)

    with pytest.raises(ValueError, match="forbidden field: support_contact_id"):
        update_event(
            session=session,
            event_id=1,
            support_contact_id=2,
        )


def test_update_event_rejects_missing_title(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="title is required"):
        update_event(
            session=session,
            event_id=1,
            title="",
        )


def test_update_event_rejects_missing_location(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="location is required"):
        update_event(
            session=session,
            event_id=1,
            location="",
        )


def test_update_event_rejects_missing_attendees(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="attendees is required"):
        update_event(
            session=session,
            event_id=1,
            attendees=None,
        )


def test_update_event_rejects_invalid_attendees_type(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="attendees must be an integer"):
        update_event(
            session=session,
            event_id=1,
            attendees="99",
        )


def test_update_event_rejects_negative_attendees(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="attendees must be greater than or equal to 0"):
        update_event(
            session=session,
            event_id=1,
            attendees=-1,
        )


def test_update_event_rejects_missing_date_start(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="date_start is required"):
        update_event(
            session=session,
            event_id=1,
            date_start=None,
        )


def test_update_event_rejects_invalid_date_start_type(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="date_start must be a datetime"):
        update_event(
            session=session,
            event_id=1,
            date_start="2025-01-01",
        )


def test_update_event_rejects_missing_date_end(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="date_end is required"):
        update_event(
            session=session,
            event_id=1,
            date_end=None,
        )


def test_update_event_rejects_invalid_date_end_type(session, seeded_events, monkeypatch):

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="date_end must be a datetime"):
        update_event(
            session=session,
            event_id=1,
            date_end="2025-01-01",
        )


def test_update_event_rejects_date_end_before_date_start_when_only_date_end_changes(session, seeded_events, monkeypatch):
    earlier_end = datetime.now() - timedelta(hours=1)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="date_end must be greater than or equal to date_start"):
        update_event(
            session=session,
            event_id=1,
            date_end=earlier_end,
        )


def test_update_event_rejects_date_end_before_date_start_when_both_change(session, seeded_events, monkeypatch):
    start = datetime.now()
    end = start - timedelta(hours=1)

    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: support_user)

    with pytest.raises(ValueError, match="date_end must be greater than or equal to date_start"):
        update_event(
            session=session,
            event_id=1,
            date_start=start,
            date_end=end,
        )