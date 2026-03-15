import click

from epicevents.auth.login import login
from epicevents.auth.logout import logout



@click.group()
def cli():
    """CLI Epic Events."""
    pass

@cli.command(name="login")
def login_command():
    """Login to the application."""
    email = click.prompt("Email")
    password = click.prompt("Password", hide_input=True)
    try:
        login(email, password)
        click.echo("Login successful")
    except Exception as e:
        click.echo(f"Login failed: {e}", err=True)

@cli.command(name="logout")
def logout_command():
    """Logout from the application."""
    try:
        logout()
        click.echo("Logout successful")
    except Exception as e:
        click.echo(f"Logout failed: {e}", err=True)
