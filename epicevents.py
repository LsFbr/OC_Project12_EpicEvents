from epicevents.monitoring.sentry import init_sentry
from epicevents.cli.cli import cli


def main():
    init_sentry()
    cli()


if __name__ == "__main__":
    main()