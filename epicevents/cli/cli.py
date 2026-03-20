import click

from epicevents.db.session import SessionLocal

from epicevents.auth.login import login
from epicevents.auth.logout import logout
from epicevents.services.collaborators import (
get_all_collaborators, create_collaborator, update_collaborator, delete_collaborator
)
from epicevents.services.clients import (
    get_all_clients, create_client, update_client,
)
from epicevents.services.contracts import (
    get_all_contracts, create_contract, update_contract
)
from epicevents.cli.prompt_helpers import prompt_text, prompt_email, prompt_password, prompt_role, prompt_int, prompt_bool

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


@cli.group()
def clients():
    """Clients management."""
    pass

@clients.command(name="list")
def clients_list_command():
    """List all clients."""
    session = SessionLocal()
    try:
        clients = get_all_clients(session)

        if not clients:
            click.echo("No clients found.")
            return


        click.echo("ID | Name | Email | Phone | Company | Informations | Sales Contact ID | Sales Contact Name")
        click.echo("--------------------------------------------------------")
        for client in clients:
            informations = client.informations if client.informations else "N/A"
            click.echo(
                f"{client.id} | "
                f"{client.name} | "
                f"{client.email} | "
                f"{client.phone_number} | "
                f"{client.company_name} | "
                f"{informations} | "
                f"{client.sales_contact_id} | "
                f"{client.sales_contact.full_name}"
            )
    except Exception as e:
        click.echo(f"Clients list failed: {e}", err=True)
    finally:
        session.close()

@clients.command(name="create")
def clients_create_command():
    """Create a new client. (Requires SALES role)"""
    session = SessionLocal()
    try:
        click.echo("Enter the details for the new client (marked with * are required):")

        name = prompt_text("Name", max_length=64)
        email = prompt_email("Email")
        phone_number = prompt_text("Phone Number", max_length=20)
        company_name = prompt_text("Company Name", max_length=64)
        informations = prompt_text("Informations", required=False)

        client = create_client(
            session,
            informations,
            name,
            email,
            phone_number,
            company_name,
        )

        informations = client.informations if client.informations else "N/A"

        click.echo(f"Client {client.name} created successfully.")
        click.echo("ID | Name | Email | Phone | Company | Informations | Sales Contact ID | Sales Contact Name")
        click.echo("--------------------------------------------------------")
        click.echo(
            f"{client.id} | "
            f"{client.name} | "
            f"{client.email} | "
            f"{client.phone_number} | "
            f"{client.company_name} | "
            f"{informations} | "
            f"{client.sales_contact_id} | "
            f"{client.sales_contact.full_name}"
        )
    except Exception as e:
        click.echo(f"Clients create failed: {e}", err=True)
    finally:
        session.close()

@clients.command(name="update")
def clients_update_command():
    """Update a client. (Requires SALES role and to be the sales contact of the client)"""
    session = SessionLocal()
    try:
        click.echo("Enter the details for the client to update (marked with * are required):")
        fields = {}

        client_id = prompt_int("Client ID")
        name = prompt_text("Name", required=False, max_length=64)
        email = prompt_email("Email", required=False)
        phone_number = prompt_text("Phone Number", required=False, max_length=20)
        company_name = prompt_text("Company Name", required=False, max_length=64)
        informations = prompt_text("Informations", required=False)

        if name:
            fields["name"] = name
        if email:
            fields["email"] = email
        if phone_number:
            fields["phone_number"] = phone_number
        if company_name:
            fields["company_name"] = company_name
        if informations:
            fields["informations"] = informations

        client = update_client(session, client_id, **fields)

        informations_value = client.informations if client.informations else "N/A"
        sales_contact_id = client.sales_contact_id if client.sales_contact_id is not None else "N/A"
        sales_contact_name = (
            client.sales_contact.full_name if client.sales_contact is not None else "N/A"
        )

        click.echo(f"Client {client.name} updated successfully.")
        click.echo("ID | Name | Email | Phone | Company | Informations | Sales Contact ID | Sales Contact Name")
        click.echo("--------------------------------------------------------")
        click.echo(
            f"{client.id} | "
            f"{client.name} | "
            f"{client.email} | "
            f"{client.phone_number} | "
            f"{client.company_name} | "
            f"{informations_value} | "
            f"{sales_contact_id} | "
            f"{sales_contact_name}"
        )
    except Exception as e:
        click.echo(f"Clients update failed: {e}", err=True)
    finally:
        session.close()


@cli.group()
def contracts():
    """Contracts management."""
    pass

@contracts.command(name="list")
def contracts_list_command():
    """List all contracts."""
    session = SessionLocal()
    try:
        contracts = get_all_contracts(session)

        if not contracts:
            click.echo("No contracts found.")
            return

        click.echo("ID | Total Amount | Rest Amount | Signed | Client ID | Client Name | Support Contact ID | Support Contact Name")
        click.echo("-----------------------------------------------------------------")
        for contract in contracts:
            is_signed = "Yes" if contract.is_signed else "No"
            click.echo(
                f"{contract.id} | "
                f"{contract.total_amount} | "
                f"{contract.rest_amount} | "
                f"{is_signed} | "
                f"{contract.client_id} | "
                f"{contract.client.name} | "
                f"{contract.client.sales_contact_id} | "
                f"{contract.client.sales_contact.full_name}"
            )
    except Exception as e:
        click.echo(f"Contracts list failed: {e}", err=True)
    finally:
        session.close()

@contracts.command(name="create")
def contracts_create_command():
    """Create a new contract. (Requires SALES role and to be the sales contact of the client)"""
    session = SessionLocal()
    try:
        click.echo("Enter the details for the new contract (marked with * are required):")

        total_amount = prompt_text("Total Amount")
        rest_amount = prompt_text("Rest Amount")
        is_signed = prompt_bool("Is Signed")
        client_id = prompt_int("Client ID")

        contract = create_contract(
            session,
            client_id,
            total_amount,
            rest_amount,
            is_signed,
        )

        is_signed = "Yes" if contract.is_signed else "No"

        click.echo(f"Contract {contract.id} created successfully.")
        click.echo("ID | Total Amount | Rest Amount | Signed | Client ID | Client Name | Support Contact ID | Support Contact Name")
        click.echo("-----------------------------------------------------------------")
        click.echo(
            f"{contract.id} | "
            f"{contract.total_amount} | "
            f"{contract.rest_amount} | "
            f"{is_signed} | "
            f"{contract.client_id} | "
            f"{contract.client.name} | "
            f"{contract.client.sales_contact_id} | "
            f"{contract.client.sales_contact.full_name}"
        )
    except Exception as e:
        click.echo(f"Contracts create failed: {e}", err=True)
    finally:
        session.close()

@contracts.command(name="update")
def contracts_update_command():
    """Update a contract. (Requires SALES role and to be the sales contact of the client)"""
    session = SessionLocal()
    try:
        click.echo("Enter the details for the contract to update (marked with * are required):")
        fields = {}

        contract_id = prompt_int("Contract ID")
        total_amount = prompt_text("Total Amount", required=False)
        rest_amount = prompt_text("Rest Amount", required=False)
        is_signed = prompt_bool("Is Signed", required=False)

        if total_amount is not None:
            fields["total_amount"] = total_amount
        if rest_amount is not None:
            fields["rest_amount"] = rest_amount
        if is_signed is not None:
            fields["is_signed"] = is_signed

        contract = update_contract(session, contract_id, **fields)

        is_signed = "Yes" if contract.is_signed else "No"

        click.echo(f"Contract {contract.id} updated successfully.")
        click.echo("ID | Total Amount | Rest Amount | Signed | Client ID | Client Name | Support Contact ID | Support Contact Name")
        click.echo("-----------------------------------------------------------------")
        click.echo(
            f"{contract.id} | "
            f"{contract.total_amount} | "
            f"{contract.rest_amount} | "
            f"{is_signed} | "
            f"{contract.client_id} | "
            f"{contract.client.name} | "
            f"{contract.client.sales_contact_id} | "
            f"{contract.client.sales_contact.full_name}"
        )
    except Exception as e:
        click.echo(f"Contracts update failed: {e}", err=True)
    finally:
        session.close()