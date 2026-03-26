import os
from pathlib import Path
from datetime import datetime

import pytest


# Set the JWT secret key for the tests
os.environ["EPICEVENTS_SECRET"] = "test-secret-test-secret-test-secret"


class FakeRole:
    def __init__(self, name="fake_role"):
        self.name = name


class FakeUser:
    def __init__(
        self,
        user_id=1,
        employee_number=1,
        full_name="Test User",
        email="test@test.com",
        role_name="fake_role",
    ):
        self.id = user_id
        self.role = FakeRole(role_name)
        self.email = email
        self.full_name = full_name
        self.employee_number = employee_number
        self.password_hash = "hashed"


class FakeClient:
    def __init__(
        self,
        client_id=1,
        name="Client",
        email="client@test.com",
        phone_number="0600000000",
        company_name="Company",
        informations="Info",
        sales_contact_id=1,
    ):
        self.id = client_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.company_name = company_name
        self.informations = informations
        self.sales_contact_id = sales_contact_id


class FakeContract:
    def __init__(
        self,
        contract_id=1,
        total_amount=1000,
        rest_amount=1000,
        is_signed=True,
        client=None,
        client_id=1,
    ):
        self.id = contract_id
        self.total_amount = total_amount
        self.rest_amount = rest_amount
        self.is_signed = is_signed
        self.client = client
        self.client_id = client.id if client is not None else client_id


class FakeEvent:
    def __init__(
        self,
        event_id=1,
        title="Event",
        notes="Notes",
        location="Paris",
        attendees=10,
        date_start=None,
        date_end=None,
        contract_id=1,
        support_contact_id=None,
        support_contact=None,
    ):
        self.id = event_id
        self.title = title
        self.notes = notes
        self.location = location
        self.attendees = attendees
        self.date_start = date_start or datetime(2026, 1, 1, 9, 0)
        self.date_end = date_end or datetime(2026, 1, 1, 17, 0)
        self.contract_id = contract_id
        self.support_contact_id = support_contact_id
        self.support_contact = support_contact


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, **kwargs):
        filtered = self.items
        for key, value in kwargs.items():
            filtered = [item for item in filtered if getattr(item, key, None) == value]
        return FakeQuery(filtered)

    def options(self, *args):
        return self

    def first(self):
        return self.items[0] if self.items else None

    def one_or_none(self):
        return self.items[0] if self.items else None

    def all(self):
        return self.items


class FakeScalarResult:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


class FakeExecuteResult:
    def __init__(self, items):
        self.items = items

    def scalars(self):
        return FakeScalarResult(self.items)


class FakeSession:
    def __init__(self, query_map=None, execute_items=None):
        self.query_map = query_map or {}
        self.execute_items = execute_items or []
        self.added = []
        self.deleted = []
        self.refreshed = []
        self.committed = False
        self.closed = False

    def query(self, model):
        return FakeQuery(self.query_map.get(model, []))

    def execute(self, statement):
        return FakeExecuteResult(self.execute_items)

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = 999
        self.added.append(obj)

    def add_all(self, objects):
        for obj in objects:
            self.add(obj)

    def delete(self, obj):
        self.deleted.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed.append(obj)

    def close(self):
        self.closed = True


@pytest.fixture
def fake_user():
    return FakeUser(user_id=1, role_name="MANAGEMENT")


@pytest.fixture
def fake_session():
    return FakeSession(query_map={}, execute_items=[])


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """
    Replace Path.home() with a temporary directory.
    """
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path


@pytest.fixture
def management_user():
    return FakeUser(user_id=10, employee_number=10, full_name="Management User", email="management@test.com", role_name="MANAGEMENT")


@pytest.fixture
def sales_user():
    return FakeUser(user_id=20, employee_number=20, full_name="Sales User", email="sales@test.com", role_name="SALES")


@pytest.fixture
def support_user():
    return FakeUser(user_id=30, employee_number=30, full_name="Support User", email="support@test.com", role_name="SUPPORT")