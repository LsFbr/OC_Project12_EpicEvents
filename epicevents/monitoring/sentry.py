import os
from copy import deepcopy

import sentry_sdk
from sentry_sdk.types import Event, Hint


SENSITIVE_KEYS = {
    "password",
    "plain_password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "auth",
    "secret",
    "dsn",
    "email",
}


def _scrub_value(value):
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                cleaned[key] = "[Filtered]"
            else:
                cleaned[key] = _scrub_value(item)
        return cleaned

    if isinstance(value, list):
        return [_scrub_value(item) for item in value]

    return value


def before_send(event: Event, hint: Hint) -> Event | None:
    event = deepcopy(event)

    event.pop("server_name", None)
    event.pop("user", None)

    for key in ("extra", "contexts", "request"):
        if key in event:
            event[key] = _scrub_value(event[key])

    breadcrumbs = event.get("breadcrumbs")
    if isinstance(breadcrumbs, dict) and isinstance(breadcrumbs.get("values"), list):
        breadcrumbs["values"] = _scrub_value(breadcrumbs["values"])

    extra = event.get("extra")
    if isinstance(extra, dict) and "sys.argv" in extra:
        extra["sys.argv"] = "[Filtered]"

    return event


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        release=os.getenv("SENTRY_RELEASE"),
        send_default_pii=False,
        include_local_variables=False,
        before_send=before_send,
    )


def capture_unexpected_exception(exc: Exception, **context) -> None:
    with sentry_sdk.new_scope() as scope:
        for key, value in context.items():
            scope.set_extra(key, value)
        scope.capture_exception(exc)


def capture_business_event(message: str, **context) -> None:
    with sentry_sdk.new_scope() as scope:
        for key, value in context.items():
            scope.set_extra(key, value)
        scope.capture_message(message)