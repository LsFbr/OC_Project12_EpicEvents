from epicevents.cli.cli import cli
from epicevents.auth.token_storage import load_token


def test_login_list_logout_then_forbidden(runner, integration_env):
    """Log in as management, access a protected list command, verify that a token is stored,
    log out, verify that the token is removed, then ensure the protected command is refused."""
    result = runner.invoke(
        cli,
        ["login"],
        input="management@test.com\nPassword123\n",
    )
    assert result.exit_code == 0
    assert "Login successful" in result.output
    assert load_token() is not None

    result = runner.invoke(cli, ["clients", "list"])
    assert result.exit_code == 0
    assert "No clients found." in result.output

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0
    assert "Logout successful" in result.output
    assert load_token() is None

    result = runner.invoke(cli, ["clients", "list"])
    assert result.exit_code == 0
    assert "Clients list failed: You must login first" in result.output
