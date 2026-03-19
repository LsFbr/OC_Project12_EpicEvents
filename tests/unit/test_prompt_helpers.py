import pytest

from epicevents.cli.prompt_helpers import (
    prompt_text,
    prompt_email,
    prompt_password,
    prompt_int,
    prompt_role,
)


# tests prompt_text
def test_prompt_text_required_ok(monkeypatch):
    prompt = "User Example"
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_text("Full Name")

    assert echoed == []
    assert value == "User Example"


def test_prompt_text_required_empty_then_ok(monkeypatch):
    prompts = iter(["", "User Example"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_text("Full Name")

    assert echoed == [("Full Name is required.", True)]
    assert value == "User Example"  


def test_prompt_text_optional_empty_returns_none(monkeypatch):
    prompt = ""
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_text("Notes", required=False)

    assert echoed == []
    assert value is None


def test_prompt_text_too_long_then_ok(monkeypatch):
    prompts = iter(["Too long", "Ok"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_text("Full Name", max_length=2)

    assert echoed == [("Full Name must be at most 2 characters long.", True)]
    assert value == "Ok"


# tests prompt_email
def test_prompt_email_required_ok(monkeypatch):
    prompt = "USER@Example.com"
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_email("Email")

    assert echoed == []
    assert value == "user@example.com"


def test_prompt_email_required_empty_then_ok(monkeypatch):
    prompts = iter(["", "user@example.com"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_email("Email")

    assert echoed == [("Email is required.", True)]
    assert value == "user@example.com"


def test_prompt_email_optional_empty_returns_none(monkeypatch):
    prompt = ""
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_email("Email", required=False)

    assert echoed == []
    assert value is None


def test_prompt_email_invalid_then_ok(monkeypatch):
    prompts = iter(["not-an-email", "user@example.com"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_email("Email")

    assert echoed == [("Email is invalid.", True)]
    assert value == "user@example.com"


def test_prompt_email_too_long_then_ok(monkeypatch):
    too_long_email = ("a" * 117) + "@example.com"
    prompts = iter([too_long_email, "user@example.com"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_email("Email")

    assert echoed == [("Email must be less than 128 characters.", True)]
    assert value == "user@example.com"


# tests prompt_password
def test_prompt_password_required_ok(monkeypatch):
    prompt = "Password123"
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, hide_input, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_password("Password")

    assert echoed == []
    assert value == "Password123"


def test_prompt_password_required_empty_then_ok(monkeypatch):
    prompts = iter(["", "Password123"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, hide_input, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_password("Password")

    assert echoed == [("Password is required.", True)]
    assert value == "Password123"


def test_prompt_password_optional_empty_returns_none(monkeypatch):
    prompt = ""
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, hide_input, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_password("Password", required=False)

    assert echoed == []
    assert value is None


def test_prompt_password_too_short_then_ok(monkeypatch):
    prompts = iter(["short", "Password123"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, hide_input, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_password("Password")

    assert echoed == [("Password must be at least 8 characters long.", True)]
    assert value == "Password123"


# tests prompt_int
def test_prompt_int_required_ok(monkeypatch):
    prompt = "12"
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_int("Employee Number")

    assert echoed == []
    assert value == 12


def test_prompt_int_required_empty_then_ok(monkeypatch):
    prompts = iter(["", "12"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_int("Employee Number")

    assert echoed == [("Employee Number is required.", True)]
    assert value == 12


def test_prompt_int_optional_empty_returns_none(monkeypatch):
    prompt = ""
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_int("Employee Number", required=False)

    assert echoed == []
    assert value is None


def test_prompt_int_invalid_then_ok(monkeypatch):
    prompts = iter(["abc", "12"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_int("Employee Number")

    assert echoed == [("Employee Number must be an integer.", True)]
    assert value == 12


def test_prompt_int_negative_then_0_ok(monkeypatch):
    prompts = iter(["-1", "0"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_int("Employee Number", min_value=0)

    assert echoed == [("Employee Number must be greater than or equal to 0.", True)]
    assert value == 0

# tests prompt_role 
def test_prompt_role_required_ok(monkeypatch):
    prompt = "management"
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_role("Role")

    assert echoed == []
    assert value == "MANAGEMENT"


def test_prompt_role_required_empty_then_ok(monkeypatch):
    prompts = iter(["", "MANAGEMENT"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_role("Role")

    assert echoed == [("Role is required.", True)]
    assert value == "MANAGEMENT"


def test_prompt_role_optional_empty_returns_none(monkeypatch):
    prompt = ""
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: prompt,
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_role("Role", required=False)

    assert echoed == []
    assert value is None


def test_prompt_role_invalid_then_ok(monkeypatch):
    prompts = iter(["INVALID", "SALES"])
    echoed = []

    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.prompt",
        lambda text, default, show_default: next(prompts),
    )
    monkeypatch.setattr(
        "epicevents.cli.prompt_helpers.click.echo",
        lambda message, err: echoed.append((message, err)),
    )

    value = prompt_role("Role")

    assert echoed == [("Role must be one of: SALES, SUPPORT, MANAGEMENT.", True)]
    assert value == "SALES"
    