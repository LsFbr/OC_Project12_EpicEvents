import pytest 
from datetime import datetime

from epicevents.services.events import get_all_events
from epicevents.models.event import Event


@pytest.fixture
def seeded_events(session):
    session.add_all([
        Event(title="Event 1", location="Event 1", attendees=10, date_start=datetime.now(), date_end=datetime.now(), contract_id=1),
        Event(title="Event 2", location="Event 2", attendees=20, date_start=datetime.now(), date_end=datetime.now(), contract_id=1),
        Event(title="Event 3", location="Event 3", attendees=30, date_start=datetime.now(), date_end=datetime.now(), contract_id=1),
    ])
    session.commit()

class FakeRole:
    def __init__(self):
        self.name = "fake_role"

class FakeUser:
    def __init__(self):
        self.role = FakeRole()

def raise_authentication_failed():
    raise Exception("Authentication failed")

def raise_no_permission(role, action):
    raise Exception("No permission")

def test_get_all_events_ok(session, seeded_events, monkeypatch):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: FakeUser())
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)
    

    events = get_all_events(session)
    assert len(events) == 3
    assert events[0].title == "Event 1"
    assert events[1].title == "Event 2"
    assert events[2].title == "Event 3"


def test_get_all_events_authentication_failed(session, seeded_events, monkeypatch):
    monkeypatch.setattr("epicevents.services.events.require_authentication", raise_authentication_failed)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: FakeUser())
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)
    with pytest.raises(Exception):
        get_all_events(session)


def test_get_all_events_no_user(session, seeded_events, monkeypatch):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: None)
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)
    with pytest.raises(Exception):
        get_all_events(session)


def test_get_all_events_no_permission(session, seeded_events, monkeypatch):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: FakeUser())
    monkeypatch.setattr("epicevents.services.events.require_permission", raise_no_permission)
    with pytest.raises(Exception):
        get_all_events(session)
        

def test_get_all_events_no_events(session, monkeypatch):
    monkeypatch.setattr("epicevents.services.events.require_authentication", lambda: None)
    monkeypatch.setattr("epicevents.services.events.get_current_user", lambda: FakeUser())
    monkeypatch.setattr("epicevents.services.events.require_permission", lambda role, action: None)
    events = get_all_events(session)
    assert len(events) == 0