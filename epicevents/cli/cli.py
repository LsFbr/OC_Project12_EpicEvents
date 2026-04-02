import click

from epicevents.exceptions import AuthenticationError, BusinessValidationError, BusinessAuthorizationError
from epicevents.monitoring.sentry import capture_unexpected_exception
from epicevents.db.session import SessionLocal
from epicevents.auth.utils import require_authentication
from epicevents.auth.current_user import get_current_user
from epicevents.security.permissions import (
    require_permission, has_permission,
    READ_ALL, COLLAB_CREATE, COLLAB_UPDATE, COLLAB_DELETE,
    CLIENT_CREATE, CLIENT_UPDATE_OWNED,
    CONTRACT_CREATE, CONTRACT_UPDATE_ANY, CONTRACT_UPDATE_OWNED, 
    CONTRACT_FILTER_BY_PAID_UNPAID, CONTRACT_FILTER_BY_SIGNED_NOT_SIGNED,
    EVENT_CREATE, EVENT_UPDATE_ASSIGNED, EVENT_ASSIGN_SUPPORT,
    EVENT_FILTER_BY_SUPPORT_CONTACT_ID, EVENT_FILTER_BY_MINE,
)

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
from epicevents.services.events import (
    get_all_events, create_event, update_event, assign_support,
)
from epicevents.cli.prompt_helpers import (
    prompt_text,
    prompt_email,
    prompt_password,
    prompt_role,
    prompt_int,
    prompt_bool,
    prompt_datetime,
)

def handle_cli_error(action_label: str, exc: Exception) -> None:
    if isinstance(exc, click.Abort):
        return

    if isinstance(exc, (AuthenticationError, BusinessAuthorizationError, BusinessValidationError)):
        click.echo(f"{action_label} failed: {exc}", err=True)
        return

    capture_unexpected_exception(exc, action=action_label)
    click.echo(f"{action_label} failed: unexpected error", err=True)

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
        handle_cli_error("Login", e)

@cli.command(name="logout")
def logout_command():
    """Logout from the application."""
    try:
        logout()
        click.echo("Logout successful")
    except Exception as e:
        handle_cli_error("Logout", e)

@cli.group()
def collaborators():
    """Collaborators management."""
    pass

@collaborators.command(name="list")
def collaborators_list_command():
    """List all collaborators."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, READ_ALL)
        
        collaborators = get_all_collaborators(session)

        if not collaborators:
            click.echo("No collaborators found.")
            return

        click.echo("ID | Employee Number | Full Name | Email | Role")
        click.echo("--------------------------------------------------")
        for collaborator in collaborators:
            click.echo(
                f"{collaborator.id} | "
                f"{collaborator.employee_number} | "
                f"{collaborator.full_name} | "
                f"{collaborator.email} | "
                f"{collaborator.role.name}"
            )
    except Exception as e:
        handle_cli_error("Collaborators list", e)
    finally:
        session.close()

@collaborators.command(name="create")
def collaborators_create_command():
    """Create a new collaborator (MANAGEMENT)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, COLLAB_CREATE)

        click.echo("Enter the details for the new collaborator (marked with * are required):")

        employee_number = prompt_int("Employee Number")
        full_name = prompt_text("Full Name", max_length=64)
        email = prompt_email("Email")
        role = prompt_role("Role")
        plain_password = prompt_password("Password")
        collaborator = create_collaborator(session, employee_number, full_name, email, role, plain_password)

        click.echo(f"Collaborator {collaborator.full_name} created successfully.")
        click.echo("ID | Employee Number | Full Name | Email | Role")
        click.echo("--------------------------------------------------")
        click.echo(
            f"{collaborator.id} | "
            f"{collaborator.employee_number} | "
            f"{collaborator.full_name} | "
            f"{collaborator.email} | "
            f"{collaborator.role.name}"
        )
    except Exception as e:
        handle_cli_error("Collaborators create", e)
    finally:
        session.close()

@collaborators.command(name="update")
def collaborators_update_command():
    """Update a collaborator (MANAGEMENT)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, COLLAB_UPDATE)

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
        click.echo("ID | Employee Number | Full Name | Email | Role")
        click.echo("--------------------------------------------------")
        click.echo(
            f"{collaborator.id} | "
            f"{collaborator.employee_number} | "
            f"{collaborator.full_name} | "
            f"{collaborator.email} | "
            f"{collaborator.role.name}"
        )
    except Exception as e:
        handle_cli_error("Collaborators update", e)
    finally:
        session.close()

@collaborators.command(name="delete")
def collaborators_delete_command():
    """Delete a collaborator (MANAGEMENT)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, COLLAB_DELETE)

        click.echo("Enter the employee number of the collaborator to delete:")
        employee_number = prompt_int("Employee Number")
        collaborator = delete_collaborator(session, employee_number)
        click.echo(f"Collaborator {collaborator.full_name} deleted successfully.")
    except Exception as e:
        handle_cli_error("Collaborators delete", e)
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
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, READ_ALL)

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
        handle_cli_error("Clients list", e)
    finally:
        session.close()

@clients.command(name="create")
def clients_create_command():
    """Create a new client (SALES)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, CLIENT_CREATE)

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
        handle_cli_error("Clients create", e)
    finally:
        session.close()

@clients.command(name="update")
def clients_update_command():
    """Update a client (SALES and owner)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, CLIENT_UPDATE_OWNED)

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
        handle_cli_error("Clients update", e)
    finally:
        session.close()


@cli.group()
def contracts():
    """Contracts management."""
    pass

@contracts.command(name="list")
@click.option("--signed", is_flag=True, help="Show only signed contracts.")
@click.option("--not-signed", is_flag=True, help="Show only unsigned contracts.")
@click.option("--unpaid", is_flag=True, help="Show only contracts with a remaining balance.")
@click.option("--paid", is_flag=True, help="Show only fully paid contracts.")
def contracts_list_command(signed: bool, not_signed: bool, unpaid: bool, paid: bool):
    """List all contracts."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, READ_ALL)

        if signed and not_signed:
            raise BusinessValidationError("signed and not_signed filters cannot be used together")

        if paid and unpaid:
            raise BusinessValidationError("paid and unpaid filters cannot be used together")

        if signed and not has_permission(user.role.name, CONTRACT_FILTER_BY_SIGNED_NOT_SIGNED):
            raise BusinessAuthorizationError("only sales can filter by signed contracts")

        if not_signed and not has_permission(user.role.name, CONTRACT_FILTER_BY_SIGNED_NOT_SIGNED):
            raise BusinessAuthorizationError("only sales can filter by not signed contracts")

        if unpaid and not has_permission(user.role.name, CONTRACT_FILTER_BY_PAID_UNPAID):
            raise BusinessAuthorizationError("only sales can filter by unpaid contracts")

        if paid and not has_permission(user.role.name, CONTRACT_FILTER_BY_PAID_UNPAID):
            raise BusinessAuthorizationError("only sales can filter by paid contracts")

        contracts = get_all_contracts(
            session,
            signed=signed,
            not_signed=not_signed,
            unpaid=unpaid,
            paid=paid,
        )

        if not contracts:
            click.echo("No contracts found.")
            return

        click.echo("ID | Total Amount | Rest Amount | Signed | Client ID | Client Name | Support Contact ID | Support Contact Name")
        click.echo("-----------------------------------------------------------------")
        for contract in contracts:
            is_signed_display = "Yes" if contract.is_signed else "No"
            click.echo(
                f"{contract.id} | "
                f"{contract.total_amount} | "
                f"{contract.rest_amount} | "
                f"{is_signed_display} | "
                f"{contract.client_id} | "
                f"{contract.client.name} | "
                f"{contract.client.sales_contact_id} | "
                f"{contract.client.sales_contact.full_name}"
            )

    except Exception as e:
        handle_cli_error("Contracts list", e)
    finally:
        session.close()

@contracts.command(name="create")
def contracts_create_command():
    """Create a new contract (SALES and owner)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, CONTRACT_CREATE)

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
        handle_cli_error("Contracts create", e)
    finally:
        session.close()

@contracts.command(name="update")
def contracts_update_command():
    """Update a contract (MANAGEMENT, or SALES and owner)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()

        can_update_any = has_permission(user.role.name, CONTRACT_UPDATE_ANY)
        can_update_owned = has_permission(user.role.name, CONTRACT_UPDATE_OWNED)

        if not can_update_any and not can_update_owned:
            raise BusinessAuthorizationError("You do not have permission to update this contract")
        
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
        handle_cli_error("Contracts update", e)
    finally:
        session.close()


@cli.group()
def events():
    """Events management."""
    pass

@events.command(name="list")
@click.option("--support-contact-id", type=int, default=None, help="Filter events by support collaborator id (MANAGEMENT).")
@click.option("--mine", is_flag=True, help="Show only events assigned to the connected support collaborator.")
def events_list_command(support_contact_id: int | None, mine: bool):
    """List all events."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, READ_ALL)

        if support_contact_id is not None and not has_permission(user.role.name, EVENT_FILTER_BY_SUPPORT_CONTACT_ID):
            raise BusinessAuthorizationError("only management can filter by support contact id")

        if mine and not has_permission(user.role.name, EVENT_FILTER_BY_MINE):
            raise BusinessAuthorizationError("only support can use the mine filter")

        events = get_all_events(
            session,
            support_contact_id=support_contact_id,
            assigned_to_me=mine,
        )

        if not events:
            click.echo("No events found.")
            return

        click.echo("ID | Title | Location | Attendees | Start | End | Contract ID | Support Contact ID | Support Contact Name")
        click.echo("--------------------------------------------------------------------------------------------------------------")
        for event in events:
            support_contact_id_value = event.support_contact_id if event.support_contact_id is not None else "N/A"
            support_contact_name = (
                event.support_contact.full_name if event.support_contact is not None else "N/A"
            )

            click.echo(
                f"{event.id} | "
                f"{event.title} | "
                f"{event.location} | "
                f"{event.attendees} | "
                f"{event.date_start} | "
                f"{event.date_end} | "
                f"{event.contract_id} | "
                f"{support_contact_id_value} | "
                f"{support_contact_name}"
            )
    except Exception as e:
        handle_cli_error("Events list", e)
    finally:
        session.close()

@events.command(name="create")
def events_create_command():
    """Create a new event (SALES and owner of the signed contract)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, EVENT_CREATE)

        click.echo("Enter the details for the new event (marked with * are required):")

        title = prompt_text("Title", max_length=64)
        notes = prompt_text("Notes", required=False)
        location = prompt_text("Location", max_length=128)
        attendees = prompt_int("Attendees", min_value=0)
        date_start = prompt_datetime("Date Start")
        date_end = prompt_datetime("Date End")
        contract_id = prompt_int("Contract ID")

        event = create_event(
            session,
            title=title,
            notes=notes or "",
            location=location,
            attendees=attendees,
            date_start=date_start,
            date_end=date_end,
            contract_id=contract_id,
        )

        support_contact_id_value = event.support_contact_id if event.support_contact_id is not None else "N/A"
        support_contact_name = (
            event.support_contact.full_name if event.support_contact is not None else "N/A"
        )

        click.echo(f"Event {event.title} created successfully.")
        click.echo("ID | Title | Location | Attendees | Start | End | Contract ID | Support Contact ID | Support Contact Name")
        click.echo("--------------------------------------------------------------------------------------------------------------")
        click.echo(
            f"{event.id} | "
            f"{event.title} | "
            f"{event.location} | "
            f"{event.attendees} | "
            f"{event.date_start} | "
            f"{event.date_end} | "
            f"{event.contract_id} | "
            f"{support_contact_id_value} | "
            f"{support_contact_name}"
        )
    except Exception as e:
        handle_cli_error("Events create", e)
    finally:
        session.close()

@events.command(name="update")
def events_update_command():
    """Update an event (SUPPORT assigned to the event)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, EVENT_UPDATE_ASSIGNED)

        click.echo("Enter the details for the event to update (marked with * are required):")
        fields = {}

        event_id = prompt_int("Event ID")
        title = prompt_text("Title", required=False, max_length=64)
        notes = prompt_text("Notes", required=False)
        location = prompt_text("Location", required=False, max_length=128)
        attendees = prompt_int("Attendees", required=False, min_value=0)
        date_start = prompt_datetime("Date Start", required=False)
        date_end = prompt_datetime("Date End", required=False)

        if title is not None:
            fields["title"] = title
        if notes is not None:
            fields["notes"] = notes
        if location is not None:
            fields["location"] = location
        if attendees is not None:
            fields["attendees"] = attendees
        if date_start is not None:
            fields["date_start"] = date_start
        if date_end is not None:
            fields["date_end"] = date_end

        event = update_event(session, event_id, **fields)

        support_contact_id_value = event.support_contact_id if event.support_contact_id is not None else "N/A"
        support_contact_name = (
            event.support_contact.full_name if event.support_contact is not None else "N/A"
        )

        click.echo(f"Event {event.title} updated successfully.")
        click.echo("ID | Title | Location | Attendees | Start | End | Contract ID | Support Contact ID | Support Contact Name")
        click.echo("--------------------------------------------------------------------------------------------------------------")
        click.echo(
            f"{event.id} | "
            f"{event.title} | "
            f"{event.location} | "
            f"{event.attendees} | "
            f"{event.date_start} | "
            f"{event.date_end} | "
            f"{event.contract_id} | "
            f"{support_contact_id_value} | "
            f"{support_contact_name}"
        )
    except Exception as e:
        handle_cli_error("Events update", e)
    finally:
        session.close()

@events.command(name="assign-support")
def events_assign_support_command():
    """Assign or change the support collaborator of an event (MANAGEMENT)."""
    session = SessionLocal()
    try:
        require_authentication()
        user = get_current_user()
        require_permission(user.role.name, EVENT_ASSIGN_SUPPORT)

        click.echo("Enter the details to assign support to an event (marked with * are required):")

        event_id = prompt_int("Event ID")
        support_contact_id = prompt_int("Support Contact ID", required=False)

        event = assign_support(session, event_id, support_contact_id)

        support_contact_id_value = event.support_contact_id if event.support_contact_id is not None else "N/A"
        support_contact_name = (
            event.support_contact.full_name if event.support_contact is not None else "N/A"
        )

        click.echo(f"Support assignment updated for event {event.title}.")
        click.echo("ID | Title | Contract ID | Support Contact ID | Support Contact Name")
        click.echo("------------------------------------------------------------------")
        click.echo(
            f"{event.id} | "
            f"{event.title} | "
            f"{event.contract_id} | "
            f"{support_contact_id_value} | "
            f"{support_contact_name}"
        )
    except Exception as e:
        handle_cli_error("Events assign-support", e)
    finally:
        session.close()
