import click
import re

from epicevents.constants import PASSWORD_MIN_LENGTH, ROLE_NAMES

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def prompt_text(label: str, required: bool = True, max_length: int | None = None) -> str | None:
    """
    Prompt the user for a text input.
    Args:
        label: The label to display for the input.
        required: Whether the input is required.
        max_length: The maximum length of the input.
    Returns:
        The input value.
    """
    if required:
        prompt_label = f"{label}*"
    else:
        prompt_label = label

    while True:
        value = click.prompt(prompt_label, default="", show_default=False).strip()

        if not value:
            if required:
                click.echo(f"{label} is required.", err=True)
                continue
            return None

        if max_length is not None and len(value) > max_length:
            click.echo(f"{label} must be at most {max_length} characters long.", err=True)
            continue

        return value


def prompt_email(label: str, required: bool = True) -> str | None:
    """
    Prompt the user for an email input.
    Args:
        label: The label to display for the input.
        required: Whether the input is required.
    Returns:
        The input value.
    """
    if required:
        prompt_label = f"{label}*"
    else:
        prompt_label = label

    while True:
        value = click.prompt(prompt_label, default="", show_default=False).strip().lower()

        if not value:
            if required:
                click.echo(f"{label} is required.", err=True)
                continue
            return None

        if len(value) > 128:
            click.echo(f"{label} must be less than 128 characters.", err=True)
            continue

        if not _EMAIL_RE.match(value):
            click.echo(f"{label} is invalid.", err=True)
            continue

        return value


def prompt_password(label: str, required: bool = True) -> str | None:
    """
    Prompt the user for a password input.
    Args:
        label: The label to display for the input.
        required: Whether the input is required.
    Returns:
        The input value.
    """
    if required:
        prompt_label = f"{label}*"
    else:
        prompt_label = label

    while True:
        value = click.prompt(prompt_label, hide_input=True, default="", show_default=False).strip()

        if not value:
            if required:
                click.echo(f"{label} is required.", err=True)
                continue
            return None

        if len(value) < PASSWORD_MIN_LENGTH:
            click.echo(
                f"{label} must be at least {PASSWORD_MIN_LENGTH} characters long.",
                err=True,
            )
            continue

        return value


def prompt_int(label: str, required: bool = True, min_value: int | None = 0) -> int | None:
    """
    Prompt the user for an integer input.
    Args:
        label: The label to display for the input.
        required: Whether the input is required.
        min_value: The minimum value of the input.
    Returns:
        The input value.
    """
    if required:
        prompt_label = f"{label}*"
    else:
        prompt_label = label

    while True:
        raw = click.prompt(prompt_label, default="", show_default=False)

        if raw == "":
            if required:
                click.echo(f"{label} is required.", err=True)
                continue
            return None

        try:
            value = int(str(raw).strip())
        except ValueError:
            click.echo(f"{label} must be an integer.", err=True)
            continue

        if min_value is not None and value < min_value:
            click.echo(f"{label} must be greater than or equal to {min_value}.", err=True)
            continue

        return value


def prompt_role(label: str, required: bool = True) -> str | None:
    """
    Prompt the user for a role input.
    Args:
        label: The label to display for the input.
        required: Whether the input is required.
    Returns:
        The input value.
    """
    if required:
        prompt_label = f"{label}*"
    else:
        prompt_label = label

    while True:
        value = click.prompt(prompt_label, default="", show_default=False).strip()

        if not value:
            if required:
                click.echo(f"{label} is required.", err=True)
                continue
            return None

        if value.upper() not in ROLE_NAMES:
            click.echo(f"{label} must be one of: {', '.join(ROLE_NAMES)}.", err=True)
            continue

        return value.upper()

        #try:
        #    role_choice = click.Choice(ROLE_NAMES, case_sensitive=False)
        #    return role_choice.convert(value, None, None)
        #except click.BadParameter:
        #    click.echo(
        #        f"{label} must be one of: {', '.join(ROLE_NAMES)}.",
        #        err=True,
        #    )