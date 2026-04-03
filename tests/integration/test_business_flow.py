from epicevents.cli.cli import cli


def test_end_to_end_business_flow(runner, integration_env):
    """Run a full cross-role business flow: sales creates a client, management creates a signed contract,
    sales creates an event, management assigns support, and support lists then updates the assigned event."""
    # 1) SALES login
    result = runner.invoke(
        cli,
        ["login"],
        input="sales@test.com\nPassword123!\n",
    )
    assert result.exit_code == 0
    assert "Login successful" in result.output

    # 2) SALES create client
    result = runner.invoke(
        cli,
        ["clients", "create"],
        input=(
            "John Client\n"
            "john.client@test.com\n"
            "0601020304\n"
            "Client Corp\n"
            "Important account\n"
        ),
    )
    assert result.exit_code == 0
    assert "Client John Client created successfully." in result.output

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0

    # 3) MANAGEMENT login
    result = runner.invoke(
        cli,
        ["login"],
        input="management@test.com\nPassword123!\n",
    )
    assert result.exit_code == 0
    assert "Login successful" in result.output

    # 4) MANAGEMENT create contract for client id 1
    result = runner.invoke(
        cli,
        ["contracts", "create"],
        input=(
            "10000\n"
            "5000\n"
            "yes\n"
            "1\n"
        ),
    )
    assert result.exit_code == 0
    assert "Contract 1 created successfully." in result.output

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0

    # 5) SALES login again
    result = runner.invoke(
        cli,
        ["login"],
        input="sales@test.com\nPassword123!\n",
    )
    assert result.exit_code == 0
    assert "Login successful" in result.output

    # 6) SALES create event for signed contract id 1
    result = runner.invoke(
        cli,
        ["events", "create"],
        input=(
            "Launch Party\n"
            "Initial notes\n"
            "Paris\n"
            "50\n"
            "2026-06-01 18:00\n"
            "2026-06-01 23:00\n"
            "1\n"
        ),
    )
    assert result.exit_code == 0
    assert "Event Launch Party created successfully." in result.output

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0

    # 7) MANAGEMENT assigns support
    result = runner.invoke(
        cli,
        ["login"],
        input="management@test.com\nPassword123!\n",
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        ["events", "assign-support"],
        input=(
            "1\n"
            "3\n"
        ),
    )
    assert result.exit_code == 0
    assert "Support assignment updated for event Launch Party." in result.output

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0

    # 8) SUPPORT login
    result = runner.invoke(
        cli,
        ["login"],
        input="support@test.com\nPassword123!\n",
    )
    assert result.exit_code == 0
    assert "Login successful" in result.output

    # 9) SUPPORT lists only assigned events
    result = runner.invoke(cli, ["events", "list", "--mine"])
    assert result.exit_code == 0
    assert "Launch Party" in result.output

    # 10) SUPPORT updates assigned event
    result = runner.invoke(
        cli,
        ["events", "update"],
        input=(
            "1\n"
            "Launch Party Updated\n"
            "Updated notes\n"
            "Bordeaux\n"
            "80\n"
            "2026-06-01 19:00\n"
            "2026-06-02 00:00\n"
        ),
    )
    assert result.exit_code == 0
    assert "Event Launch Party Updated updated successfully." in result.output

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0
    assert "Logout successful" in result.output
