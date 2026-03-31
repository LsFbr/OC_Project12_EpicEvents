# tests/unit/test_sentry.py

from copy import deepcopy

from epicevents.monitoring.sentry import (
    _scrub_value,
    before_send,
    init_sentry,
    capture_unexpected_exception,
    capture_business_event,
)


class FakeScope:
    def __init__(self):
        self.extras = {}
        self.captured_exception = None
        self.captured_message = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def set_extra(self, key, value):
        self.extras[key] = value

    def capture_exception(self, exc):
        self.captured_exception = exc

    def capture_message(self, message):
        self.captured_message = message


# -------------------------
# _scrub_value
# -------------------------

def test_scrub_value_keeps_non_sensitive_values():
    value = {
        "name": "Alice",
        "role": "SALES",
        "count": 3,
    }

    cleaned = _scrub_value(value)

    assert cleaned == value


def test_scrub_value_filters_sensitive_keys_in_dict():
    value = {
        "email": "user@example.com",
        "token": "secret-token",
        "password": "Password123",
        "name": "Alice",
    }

    cleaned = _scrub_value(value)

    assert cleaned == {
        "email": "[Filtered]",
        "token": "[Filtered]",
        "password": "[Filtered]",
        "name": "Alice",
    }


def test_scrub_value_filters_nested_structures():
    value = {
        "user": {
            "email": "user@example.com",
            "profile": {
                "access_token": "abc123",
                "city": "Paris",
            },
        }
    }

    cleaned = _scrub_value(value)

    assert cleaned == {
        "user": {
            "email": "[Filtered]",
            "profile": {
                "access_token": "[Filtered]",
                "city": "Paris",
            },
        }
    }


def test_scrub_value_filters_items_inside_list():
    value = [
        {"email": "user@example.com"},
        {"token": "abc123"},
        {"name": "Alice"},
    ]

    cleaned = _scrub_value(value)

    assert cleaned == [
        {"email": "[Filtered]"},
        {"token": "[Filtered]"},
        {"name": "Alice"},
    ]


def test_scrub_value_returns_scalar_unchanged():
    assert _scrub_value("hello") == "hello"
    assert _scrub_value(123) == 123
    assert _scrub_value(None) is None


# -------------------------
# before_send
# -------------------------

def test_before_send_removes_server_name_and_user():
    event = {
        "server_name": "LouisXPS",
        "user": {"geo": {"city": "Bordeaux"}},
        "extra": {"action": "Login"},
    }

    cleaned = before_send(event, hint={})

    assert "server_name" not in cleaned
    assert "user" not in cleaned
    assert cleaned["extra"] == {"action": "Login"}


def test_before_send_filters_extra_contexts_request_and_sys_argv():
    event = {
        "extra": {
            "email": "user@example.com",
            "sys.argv": ["epicevents.py", "login"],
            "action": "Login",
        },
        "contexts": {
            "auth": {"token": "secret-token"},
            "runtime": {"name": "CPython"},
        },
        "request": {
            "headers": {"authorization": "Bearer abc123"},
            "method": "GET",
        },
    }

    cleaned = before_send(event, hint={})

    assert cleaned["extra"]["email"] == "[Filtered]"
    assert cleaned["extra"]["sys.argv"] == "[Filtered]"
    assert cleaned["extra"]["action"] == "Login"

    assert cleaned["contexts"]["auth"] == "[Filtered]"
    assert cleaned["contexts"]["runtime"]["name"] == "CPython"

    assert cleaned["request"]["headers"]["authorization"] == "[Filtered]"
    assert cleaned["request"]["method"] == "GET"


def test_before_send_filters_breadcrumbs_values():
    event = {
        "breadcrumbs": {
            "values": [
                {"message": "ok"},
                {"message": {"token": "secret-token"}},
                {"data": {"email": "user@example.com"}},
            ]
        }
    }

    cleaned = before_send(event, hint={})

    assert cleaned["breadcrumbs"]["values"][0]["message"] == "ok"
    assert cleaned["breadcrumbs"]["values"][1]["message"]["token"] == "[Filtered]"
    assert cleaned["breadcrumbs"]["values"][2]["data"]["email"] == "[Filtered]"


def test_before_send_does_not_mutate_original_event():
    event = {
        "server_name": "LouisXPS",
        "user": {"geo": {"city": "Bordeaux"}},
        "extra": {"email": "user@example.com"},
    }
    original = deepcopy(event)

    cleaned = before_send(event, hint={})

    assert event == original
    assert "server_name" not in cleaned
    assert "user" not in cleaned
    assert cleaned["extra"]["email"] == "[Filtered]"


# -------------------------
# init_sentry
# -------------------------

def test_init_sentry_does_nothing_without_dsn(monkeypatch):
    called = {}

    monkeypatch.delenv("SENTRY_DSN", raising=False)
    monkeypatch.setattr("epicevents.monitoring.sentry.sentry_sdk.init", lambda **kwargs: called.update(kwargs))

    init_sentry()

    assert called == {}


def test_init_sentry_calls_sdk_init_with_expected_arguments(monkeypatch):
    called = {}

    monkeypatch.setenv("SENTRY_DSN", "https://example_dsn")
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "development")
    monkeypatch.setenv("SENTRY_RELEASE", "epicevents@0.1.0")

    def fake_init(**kwargs):
        called.update(kwargs)

    monkeypatch.setattr("epicevents.monitoring.sentry.sentry_sdk.init", fake_init)

    init_sentry()

    assert called["dsn"] == "https://example_dsn"
    assert called["environment"] == "development"
    assert called["release"] == "epicevents@0.1.0"
    assert called["send_default_pii"] is False
    assert called["include_local_variables"] is False
    assert called["before_send"] is before_send


# -------------------------
# capture_unexpected_exception
# -------------------------

def test_capture_unexpected_exception_sets_context_and_captures_exception(monkeypatch):
    fake_scope = FakeScope()

    monkeypatch.setattr(
        "epicevents.monitoring.sentry.sentry_sdk.new_scope",
        lambda: fake_scope,
    )

    exc = RuntimeError("boom")

    capture_unexpected_exception(exc, action="Login", contract_id=12)

    assert fake_scope.extras == {
        "action": "Login",
        "contract_id": 12,
    }
    assert fake_scope.captured_exception is exc
    assert fake_scope.captured_message is None


# -------------------------
# capture_business_event
# -------------------------

def test_capture_business_event_sets_context_and_captures_message(monkeypatch):
    fake_scope = FakeScope()

    monkeypatch.setattr(
        "epicevents.monitoring.sentry.sentry_sdk.new_scope",
        lambda: fake_scope,
    )

    capture_business_event(
        "collaborator_created",
        collaborator_id=9,
        employee_number=50,
        role_name="SALES",
    )

    assert fake_scope.extras == {
        "collaborator_id": 9,
        "employee_number": 50,
        "role_name": "SALES",
    }
    assert fake_scope.captured_message == "collaborator_created"
    assert fake_scope.captured_exception is None