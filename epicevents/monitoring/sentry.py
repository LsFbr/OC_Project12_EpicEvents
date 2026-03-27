import os

import sentry_sdk


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        release=os.getenv("SENTRY_RELEASE"),
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