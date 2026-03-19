import click

from epicevents.db.session import SessionLocal

from epicevents.auth.login import login
from epicevents.auth.logout import logout
from epicevents.services.collaborators import (
get_all_collaborators, create_collaborator, update_collaborator, delete_collaborator
)
from epicevents.cli.prompt_helpers import prompt_text, prompt_email, prompt_password, prompt_role, prompt_int

@click.group()
def cli():
    """CLI Epic Events."""
    pass

@cli.command(name="login")
def login_command():
    """Login to the application."""
    email = prompt_email("Email")
    password = prompt_password("Password")
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

@cli.group()
def collaborators():
    """Collaborators management."""
    pass

@collaborators.command(name="list")
def collaborators_list_command():
    """List all collaborators."""
    session = SessionLocal()
    try:
        collaborators = get_all_collaborators(session)

        if not collaborators:
            click.echo("No collaborators found.")
            return

        click.echo("Employee Number | Full Name | Email | Role")
        click.echo("--------------------------------------------------")
        for collaborator in collaborators:
            click.echo(
                f"{collaborator.employee_number} | "
                f"{collaborator.full_name} | "
                f"{collaborator.email} | "
                f"{collaborator.role.name}"
            )
    except Exception as e:
        click.echo(f"Collaborators list failed: {e}", err=True)
    finally:
        session.close()

@collaborators.command(name="create")
def collaborators_create_command():
    """Create a new collaborator. (Requires MANAGEMENT role)"""
    session = SessionLocal()
    try:
        click.echo("Enter the details for the new collaborator (marked with * are required):")

        employee_number = prompt_int("Employee Number")
        full_name = prompt_text("Full Name", max_length=64)
        email = prompt_email("Email")
        role = prompt_role("Role")
        plain_password = prompt_password("Password")
        collaborator = create_collaborator(session, employee_number, full_name, email, role, plain_password)

        click.echo(f"Collaborator {collaborator.full_name} created successfully.")
        click.echo("Employee Number | Full Name | Email | Role")
        click.echo("--------------------------------------------------")
        click.echo(
            f"{collaborator.employee_number} | "
            f"{collaborator.full_name} | "
            f"{collaborator.email} | "
            f"{collaborator.role.name}"
        )
    except Exception as e:
        click.echo(f"Collaborators create failed: {e}", err=True)
    finally:
        session.close()

@collaborators.command(name="update")
def collaborators_update_command():
    """Update a collaborator. (Requires MANAGEMENT role)"""
    session = SessionLocal()
    try:
        click.echo("Enter the details for the collaborator to update (marked with * are required):")
        fields = {}
        employee_number = prompt_int("Employee Number")
        full_name = prompt_text("Full Name", required=False, max_length=64)
        email = prompt_email("Email", required=False)
        role = prompt_role("Role", required=False)
        plain_password = prompt_password("Password", required=False)

        if full_name:
            fields["full_name"] = full_name
        if email:
            fields["email"] = email
        if role:
            fields["role_name"] = role
        if plain_password:
            fields["plain_password"] = plain_password

        collaborator = update_collaborator(session, employee_number, **fields)
        click.echo(f"Collaborator {collaborator.full_name} updated successfully.")
        click.echo("Employee Number | Full Name | Email | Role")
        click.echo("--------------------------------------------------")
        click.echo(
            f"{collaborator.employee_number} | "
            f"{collaborator.full_name} | "
            f"{collaborator.email} | "
            f"{collaborator.role.name}"
        )
    except Exception as e:
        click.echo(f"Collaborators update failed: {e}", err=True)
    finally:
        session.close()

@collaborators.command(name="delete")
def collaborators_delete_command():
    """Delete a collaborator. (Requires MANAGEMENT role)"""
    session = SessionLocal()
    try:
        click.echo("Enter the employee number of the collaborator to delete:")
        employee_number = prompt_int("Employee Number")
        collaborator = delete_collaborator(session, employee_number)
        click.echo(f"Collaborator {collaborator.full_name} deleted successfully.")
    except Exception as e:
        click.echo(f"Collaborators delete failed: {e}", err=True)
    finally:
        session.close()