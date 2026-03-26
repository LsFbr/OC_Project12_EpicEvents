from datetime import datetime
from epicevents.cli.cli import cli
from epicevents.models.client import Client
from epicevents.models.contract import Contract
from epicevents.models.event import Event


def test_support_cannot_create_client(runner, integration_env):
    """Log in as support, attempt to create a client, ensure the action is rejected,
    verify that no client is written to the database, then log out."""
    result = runner.invoke(
        cli,
        ["login"],
        input="support@test.com\nPassword123\n",
    )
    assert result.exit_code == 0
    assert "Login successful" in result.output

    result = runner.invoke(
        cli,
        ["clients", "create"],
        input=(
            "Forbidden Client\n"
            "forbidden.client@test.com\n"
            "0600000000\n"
            "Forbidden Corp\n"
            "Should not be created\n"
        ),
    )
    assert result.exit_code == 0
    assert "Clients create failed" in result.output

    session = integration_env["SessionLocal"]()
    try:
        clients = session.query(Client).all()
        assert len(clients) == 0
    finally:
        session.close()

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0
    assert "Logout successful" in result.output


def test_sales_cannot_assign_support(runner, integration_env):
    """Prepare a valid event, log in as sales, attempt to assign support to the event,
    verify that the action is rejected and that the support assignment remains unchanged, then log out."""
    session = integration_env["SessionLocal"]()
    try:
        contract = Contract(
            total_amount=10000,
            rest_amount=5000,
            is_signed=True,
            client_id=1,
        )
        session.add(contract)
        session.commit()

        event = Event(
            title="Sales Forbidden Assignment",
            notes="Test notes",
            location="Paris",
            attendees=10,
            date_start=datetime(2026, 6, 1, 18, 0, 0),
            date_end=datetime(2026, 6, 1, 20, 0, 0),
            contract_id=contract.id,
            support_contact_id=None,
        )
        session.add(event)
        session.commit()
        event_id = event.id
    finally:
        session.close()

    result = runner.invoke(
        cli,
        ["login"],
        input="sales@test.com\nPassword123\n",
    )
    assert result.exit_code == 0
    assert "Login successful" in result.output

    result = runner.invoke(
        cli,
        ["events", "assign-support"],
        input=f"{event_id}\n3\n",
    )
    assert result.exit_code == 0
    assert "Events assign-support failed" in result.output

    session = integration_env["SessionLocal"]()
    try:
        event = session.query(Event).filter_by(id=event_id).first()
        assert event is not None
        assert event.support_contact_id is None
    finally:
        session.close()

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0
    assert "Logout successful" in result.output


def test_management_cannot_create_event(runner, integration_env):
    """Prepare a signed contract, log in as management, attempt to create an event,
    verify that the action is rejected and that no event is written to the database, then log out."""
    session = integration_env["SessionLocal"]()
    try:
        contract = Contract(
            total_amount=12000,
            rest_amount=6000,
            is_signed=True,
            client_id=1,
        )
        session.add(contract)
        session.commit()
    finally:
        session.close()

    result = runner.invoke(
        cli,
        ["login"],
        input="management@test.com\nPassword123\n",
    )
    assert result.exit_code == 0
    assert "Login successful" in result.output

    result = runner.invoke(
        cli,
        ["events", "create"],
        input=(
            "Forbidden Event\n"
            "Forbidden notes\n"
            "Paris\n"
            "25\n"
            "2026-06-10 18:00\n"
            "2026-06-10 22:00\n"
            "1\n"
        ),
    )
    assert result.exit_code == 0
    assert "Events create failed" in result.output

    session = integration_env["SessionLocal"]()
    try:
        events = session.query(Event).all()
        assert len(events) == 0
    finally:
        session.close()

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0
    assert "Logout successful" in result.output