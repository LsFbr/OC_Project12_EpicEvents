from click.testing import CliRunner
import click

from epicevents.cli.prompt_helpers import (
    prompt_text,
    prompt_email,
    prompt_password,
    prompt_int,
    prompt_role,
)

# tests prompt_text
def test_prompt_text_required_ok():
    @click.command()
    def cmd():
        value = prompt_text("Full Name")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="User Example\n")

    assert result.exit_code == 0
    assert "VALUE=User Example" in result.output


def test_prompt_text_required_empty_then_ok():
    @click.command()
    def cmd():
        value = prompt_text("Full Name")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="\nUser Example\n")

    assert result.exit_code == 0
    assert "Full Name is required." in result.output
    assert "VALUE=User Example" in result.output


def test_prompt_text_required_too_long_then_ok():
    @click.command()
    def cmd():
        value = prompt_text("Full Name", max_length=1)
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="User Example\na\n")

    assert result.exit_code == 0
    assert "Full Name must be at most 1 characters long." in result.output
    assert "VALUE=a" in result.output

def test_prompt_text_not_required_empty_ok():
    @click.command()
    def cmd():
        value = prompt_text("Full Name", required=False)
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="\n")

    assert result.exit_code == 0
    assert "VALUE=" in result.output


# tests prompt_email
def test_prompt_email_required_ok():
    @click.command()
    def cmd():
        value = prompt_email("Email")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="user@example.com\n")

    assert result.exit_code == 0
    assert "VALUE=user@example.com" in result.output


def test_prompt_email_required_empty_then_ok():
    @click.command()
    def cmd():
        value = prompt_email("Email")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="\nuser@example.com\n")

    assert result.exit_code == 0
    assert "Email is required." in result.output
    assert "VALUE=user@example.com" in result.output

def test_prompt_email_required_too_long_then_ok():
    @click.command()
    def cmd():
        value = prompt_email("Email")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="a" * 129 + "\nuser@example.com\n")

    assert result.exit_code == 0
    assert "Email must be less than 128 characters." in result.output
    assert "VALUE=user@example.com" in result.output

def test_prompt_email_invalid_then_ok():
    @click.command()
    def cmd():
        value = prompt_email("Email")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="not-an-email\nuser@example.com\n")

    assert result.exit_code == 0
    assert "Email is invalid." in result.output
    assert "VALUE=user@example.com" in result.output

def test_prompt_email_not_required_empty_ok():
    @click.command()
    def cmd():
        value = prompt_email("Email", required=False)
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="\n")

    assert result.exit_code == 0
    assert "VALUE=" in result.output


#tests prompt_password
def test_prompt_password_required_ok():
    @click.command()
    def cmd():
        value = prompt_password("Password")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="password\n")

    assert result.exit_code == 0
    assert "VALUE=password" in result.output


def test_prompt_password_required_empty_then_ok():
    @click.command()
    def cmd():
        value = prompt_password("Password")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="\npassword\n")

    assert result.exit_code == 0
    assert "Password is required." in result.output
    assert "VALUE=password" in result.output


def test_prompt_password_required_too_short_then_ok():
    @click.command()
    def cmd():
        value = prompt_password("Password")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="a\npassword\n")

    assert result.exit_code == 0
    assert "Password must be at least 8 characters long." in result.output
    assert "VALUE=password" in result.output


def test_prompt_password_not_required_empty_ok():
    @click.command()
    def cmd():
        value = prompt_password("Password", required=False)
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="\n")

    assert result.exit_code == 0
    assert "VALUE=" in result.output


#tests prompt_int
def test_prompt_int_required_ok():
    @click.command()
    def cmd():
        value = prompt_int("Employee Number")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="1\n")

    assert result.exit_code == 0
    assert "VALUE=1" in result.output



def test_prompt_int_invalid_then_ok():
    @click.command()
    def cmd():
        value = prompt_int("Employee Number")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="a\n1\n")

    assert result.exit_code == 0
    assert "Employee Number must be an integer." in result.output
    assert "VALUE=1" in result.output


def test_prompt_int_negative_then_0_ok():
    @click.command()
    def cmd():
        value = prompt_int("Employee Number")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="-1\n0\n")

    assert result.exit_code == 0
    assert "Employee Number must be greater than or equal to 0." in result.output
    assert "VALUE=0" in result.output

def test_prompt_int_not_required_empty_ok():
    @click.command()
    def cmd():
        value = prompt_int("Employee Number", required=False)
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="\n")

    assert result.exit_code == 0
    assert "VALUE=" in result.output


#tests prompt_role
def test_prompt_role_required_ok():
    @click.command()
    def cmd():
        value = prompt_role("Role")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="MANAGEMENT\n")

    assert result.exit_code == 0
    assert "VALUE=MANAGEMENT" in result.output

def test_prompt_role_required_empty_then_ok():
    @click.command()
    def cmd():
        value = prompt_role("Role")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="\nMANAGEMENT\n")

    assert result.exit_code == 0
    assert "Role is required." in result.output
    assert "VALUE=MANAGEMENT" in result.output

def test_prompt_role_invalid_then_ok():
    @click.command()
    def cmd():
        value = prompt_role("Role")
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="INVALID\nMANAGEMENT\n")

    assert result.exit_code == 0
    assert "Role must be one of:" in result.output
    assert "VALUE=MANAGEMENT" in result.output


def test_prompt_role_not_required_empty_ok():
    @click.command()
    def cmd():
        value = prompt_role("Role", required=False)
        click.echo(f"VALUE={value}")

    runner = CliRunner()
    result = runner.invoke(cmd, input="\n")

    assert result.exit_code == 0
    assert "VALUE=" in result.output