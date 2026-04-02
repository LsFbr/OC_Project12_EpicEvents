from datetime import datetime

from epicevents.cli.prompt_helpers import (
    prompt_text,
    prompt_email,
    prompt_password,
    prompt_int,
    prompt_role,
    prompt_bool,
    prompt_datetime,
)


def capture_echo(monkeypatch):
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err=False: echoed.append((message, err)),
    )

    return echoed


# -------------------------
# prompt_text
# -------------------------

def test_prompt_text_required_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "User Example",
    )

    value = prompt_text("Full Name")

    assert echoed == []
    assert value == "User Example"


def test_prompt_text_required_empty_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["", "User Example"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_text("Full Name")

    assert echoed == [("Full Name is required.", True)]
    assert value == "User Example"


def test_prompt_text_optional_empty_returns_none(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "",
    )

    value = prompt_text("Notes", required=False)

    assert echoed == []
    assert value is None


def test_prompt_text_too_long_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["Too long", "Ok"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_text("Full Name", max_length=2)

    assert echoed == [("Full Name must be at most 2 characters long.", True)]
    assert value == "Ok"


# -------------------------
# prompt_email
# -------------------------

def test_prompt_email_required_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "USER@Example.com",
    )

    value = prompt_email("Email")

    assert echoed == []
    assert value == "user@example.com"


def test_prompt_email_required_empty_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["", "user@example.com"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_email("Email")

    assert echoed == [("Email is required.", True)]
    assert value == "user@example.com"


def test_prompt_email_optional_empty_returns_none(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "",
    )

    value = prompt_email("Email", required=False)

    assert echoed == []
    assert value is None


def test_prompt_email_invalid_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["not-an-email", "user@example.com"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_email("Email")

    assert echoed == [("Email is invalid.", True)]
    assert value == "user@example.com"


def test_prompt_email_too_long_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    too_long_email = ("a" * 117) + "@example.com"
    prompts = iter([too_long_email, "user@example.com"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_email("Email")

    assert echoed == [("Email must be less than 128 characters.", True)]
    assert value == "user@example.com"


# -------------------------
# prompt_password
# -------------------------

def test_prompt_password_required_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "Password123",
    )

    value = prompt_password("Password")

    assert echoed == []
    assert value == "Password123"


def test_prompt_password_required_empty_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["", "Password123"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_password("Password")

    assert echoed == [("Password is required.", True)]
    assert value == "Password123"


def test_prompt_password_optional_empty_returns_none(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "",
    )

    value = prompt_password("Password", required=False)

    assert echoed == []
    assert value is None


def test_prompt_password_too_short_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["short", "Password123"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_password("Password")

    assert echoed == [("Password must be at least 8 characters long.", True)]
    assert value == "Password123"


# -------------------------
# prompt_int
# -------------------------

def test_prompt_int_required_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "12",
    )

    value = prompt_int("Employee Number")

    assert echoed == []
    assert value == 12


def test_prompt_int_required_empty_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["", "12"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_int("Employee Number")

    assert echoed == [("Employee Number is required.", True)]
    assert value == 12


def test_prompt_int_optional_empty_returns_none(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "",
    )

    value = prompt_int("Employee Number", required=False)

    assert echoed == []
    assert value is None


def test_prompt_int_invalid_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["abc", "12"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_int("Employee Number")

    assert echoed == [("Employee Number must be an integer.", True)]
    assert value == 12


def test_prompt_int_negative_then_zero_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["-1", "0"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_int("Employee Number", min_value=0)

    assert echoed == [("Employee Number must be greater than or equal to 0.", True)]
    assert value == 0


# -------------------------
# prompt_role
# -------------------------

def test_prompt_role_required_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "management",
    )

    value = prompt_role("Role")

    assert echoed == []
    assert value == "MANAGEMENT"


def test_prompt_role_required_empty_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["", "MANAGEMENT"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_role("Role")

    assert echoed == [("Role is required.", True)]
    assert value == "MANAGEMENT"


def test_prompt_role_optional_empty_returns_none(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "",
    )

    value = prompt_role("Role", required=False)

    assert echoed == []
    assert value is None


def test_prompt_role_invalid_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["INVALID", "SALES"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_role("Role")

    assert echoed == [("Role must be one of: SALES, SUPPORT, MANAGEMENT.", True)]
    assert value == "SALES"


# -------------------------
# prompt_bool
# -------------------------

def test_prompt_bool_required_yes_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "yes",
    )

    value = prompt_bool("Is Signed")

    assert echoed == []
    assert value is True


def test_prompt_bool_required_no_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "no",
    )

    value = prompt_bool("Is Signed")

    assert echoed == []
    assert value is False


def test_prompt_bool_required_empty_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["", "yes"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_bool("Is Signed")

    assert echoed == [("Is Signed is required.", True)]
    assert value is True


def test_prompt_bool_optional_empty_returns_none(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "",
    )

    value = prompt_bool("Is Signed", required=False)

    assert echoed == []
    assert value is None


def test_prompt_bool_invalid_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["maybe", "no"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_bool("Is Signed")

    assert echoed == [("Is Signed must be yes or no.", True)]
    assert value is False


# -------------------------
# prompt_datetime
# -------------------------

def test_prompt_datetime_required_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "2026-01-15 14:30",
    )

    value = prompt_datetime("Date Start")

    assert echoed == []
    assert value == datetime(2026, 1, 15, 14, 30)


def test_prompt_datetime_required_empty_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["", "2026-01-15 14:30"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_datetime("Date Start")

    assert echoed == [("Date Start is required.", True)]
    assert value == datetime(2026, 1, 15, 14, 30)


def test_prompt_datetime_optional_empty_returns_none(monkeypatch):
    echoed = capture_echo(monkeypatch)

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: "",
    )

    value = prompt_datetime("Date Start", required=False)

    assert echoed == []
    assert value is None


def test_prompt_datetime_invalid_then_ok(monkeypatch):
    echoed = capture_echo(monkeypatch)
    prompts = iter(["15/01/2026 14:30", "2026-01-15 14:30"])

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda *args, **kwargs: next(prompts),
    )

    value = prompt_datetime("Date Start")

    assert echoed == [("Date Start must match format YYYY-MM-DD HH:MM.", True)]
    assert value == datetime(2026, 1, 15, 14, 30)
