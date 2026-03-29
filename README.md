# Epic Events CRM

Secure command-line CRM application developed in Python as part of the OpenClassrooms project **Develop a Secure Backend with Python and SQL**.

## 1. Project Overview

Epic Events is a company specialized in organizing events for its clients. The purpose of this project is to build a first internal CRM version to securely manage:

* collaborators
* clients
* contracts
* events

The application is designed to be used **from the command line only** and enforces access rules based on the logged-in collaborator's role.

## 2. Project Goals

This project was built to meet the following requirements:

* authenticate collaborators
* manage permissions according to the **management**, **sales**, and **support** departments
* allow secure reading, creation, and updating of data
* prevent SQL injection by using an ORM
* log unexpected errors and exceptions with **Sentry**

## 3. Main Features

### Authentication

* login through the CLI
* persistent authentication using JWT
* logout

### Ressources Management

The application allows users to manage company resources according to the permissions granted by the collaborator's role.

* list resources (with filtering options when applicable)
* create resources
* update resources
* delete resources (only applicable to ressource collaborator)

### Logging

* send unexpected exceptions to Sentry
* log critical actions defined in the project requirements

## 4. Tech Stack

* **Python 3.9+**
* **MySQL** as the relational database
* **SQLAlchemy** as the ORM
* **Click** for the command-line interface
* **PyJWT** for authentication tokens
* **Argon2** for password hashing
* **Sentry SDK** for logging and monitoring

## 5. Project Architecture

The project is organized by responsibility:

* `epicevents/models/` : SQLAlchemy models
* `epicevents/db/` : database connection, session, initialization
* `epicevents/auth/` : authentication, JWT, token storage
* `epicevents/services/` : business logic and permission checks
* `epicevents/cli/` : command-line interface
* `tests/` : unit and integration tests

This separation makes it easier to distinguish:

* data access
* business logic
* user interface
* security concerns

## 6. Security

This project was developed with the security requirements of the specification in mind.

### Password Storage

Passwords are never stored in plain text.
They are hashed with **Argon2**, which is a strong algorithm designed for secure password storage.

### Authentication

Authentication relies on a **JWT** generated at login.
This token is used to identify the current user and authorize access to protected actions.

### Authorization

Authorization is handled separately from authentication.
Each collaborator has a role, and each role grants a specific set of permissions.

### SQL Injection Prevention

The application uses **SQLAlchemy** to interact with the database, which avoids unsafe raw SQL string concatenation and promotes parameterized ORM-based access.

### Principle of Least Privilege

Access is limited according to business needs:

* all collaborators can read data
* only authorized roles can create, update, or delete specific resources
* sales collaborators can only update the clients and contracts within their scope
* support collaborators can only update events assigned to them

### Logging and Monitoring

Unexpected exceptions and specific critical actions are logged with **Sentry**.
Sensitive credentials must never be committed to the repository.

## 7. Data Model

The application is based on the following entities:

* **Role**
* **Collaborator**
* **Client**
* **Contract**
* **Event**

Main relationships:

* a collaborator belongs to a role
* a client is linked to a sales collaborator
* a contract belongs to a client
* an event belongs to a contract
* an event can be assigned to a support collaborator

## 8. Database Schema

[See the database schema (PDF)](docs/EpicEvents_Database_Schema.pdf)



## 9. Prerequisites

Before running the project, make sure you have:

* Python **3.9** or higher
* MySQL Server installed and running on your machine
* the MySQL command-line client available, or MySQL Workbench
* Git
* a Python virtual environment

> Note: the SQL commands shown in this README are the same on Windows, macOS, and Linux. What changes between operating systems is mostly the way MySQL is installed and how the `mysql` command becomes available in your terminal.

## 10. Installation

### 1. Clone the repository

```bash
git clone https://github.com/LsFbr/OC_Project12_EpicEvents.git
cd OC_Project12_EpicEvents
```

### 2. Create and activate a virtual environment

On Windows:

```bash
python -m venv venv_epicevents
venv_epicevents\Scripts\activate
```

On macOS / Linux:

```bash
python3 -m venv venv_epicevents
source venv_epicevents/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 11. Create the MySQL Database

Make sure MySQL Server is installed and running on your machine before continuing.
These SQL commands are the same on Windows, macOS, and Linux.

Connect to MySQL with an administrator account:

```bash
mysql -u root -p
```

Then run:

```sql
CREATE DATABASE EpicEventsBase
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER 'epicevents_user'@'localhost' IDENTIFIED BY 'change_this_password';
-- Creates a dedicated user for the application instead of using root.

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES
ON EpicEventsBase.*
TO 'epicevents_user'@'localhost';
-- Grants this user only the permissions needed on EpicEventsBase.

FLUSH PRIVILEGES;
```

Then update your `.env` file so that `DB_URL` matches the database name, username, password, and host you created.

Example:

```env
DB_URL=mysql+pymysql://epicevents_user:change_this_password@localhost/EpicEventsBase
```

The database must exist before running the initialization script.
The Python initialization script creates the tables and bootstrap data inside this database.

## 12. Configuration

Create a `.env` file from `.env_template`.

On Windows:

```bash
copy .env_template .env
```

On macOS / Linux:

```bash
cp .env_template .env
```

Then fill in the required environment variables.

### Environment Variables

* `DB_URL`: full SQLAlchemy database connection URL used by the application.
* `DB_USER`: database username.
* `DB_PASSWORD`: database user password.
* `DB_HOST`: database host.
* `DB_NAME`: database name.
* `EPICEVENTS_SECRET`: secret key used to sign JWTs.
* `BOOTSTRAP_MANAGEMENT_EMPLOYEE_NUMBER`: employee number of the initial management user created during database initialization.
* `BOOTSTRAP_MANAGEMENT_FULL_NAME`: full name of the initial management user.
* `BOOTSTRAP_MANAGEMENT_EMAIL`: email address of the initial management user.
* `BOOTSTRAP_MANAGEMENT_PASSWORD`: password of the initial management user.
* `SENTRY_DSN`: Sentry project DSN.
* `SENTRY_ENVIRONMENT`: Sentry environment name, for example `development`.
* `SENTRY_RELEASE`: Sentry release identifier, for example `epicevents@0.1.0`.

Example:

```env
DB_URL=mysql+pymysql://epicevents_user:change_this_password@localhost/EpicEventsBase
DB_USER=epicevents_user
DB_PASSWORD=change_this_password
DB_HOST=localhost
DB_NAME=EpicEventsBase

EPICEVENTS_SECRET=replace_with_a_long_random_secret

BOOTSTRAP_MANAGEMENT_EMPLOYEE_NUMBER=M001
BOOTSTRAP_MANAGEMENT_FULL_NAME=Admin Epic Events
BOOTSTRAP_MANAGEMENT_EMAIL=admin@epicevents.local
BOOTSTRAP_MANAGEMENT_PASSWORD=ChangeMe123!

SENTRY_DSN=your_sentry_dsn_here
SENTRY_ENVIRONMENT=development
SENTRY_RELEASE=epicevents@0.1.0
```

## 13. Database Initialization

Once the environment is configured, run the initialization script:

```bash
python -m epicevents.db.init_db
```

This script will:

* create the database tables
* insert the default roles
* create the initial management user

## 14. Running the Application

The CLI application can be launched with:

```bash
python epicevents.py
```

To display the help message:

```bash
python epicevents.py --help
```

## 15. Usage

### Login

```bash
python epicevents.py login
```

### Logout

```bash
python epicevents.py logout
```

### Example Commands

#### Collaborators

```bash
python epicevents.py collaborators list
python epicevents.py collaborators create
python epicevents.py collaborators update
python epicevents.py collaborators delete
```

#### Clients

```bash
python epicevents.py clients list
python epicevents.py clients create
python epicevents.py clients update
```

#### Contracts

```bash
python epicevents.py contracts list (options: --signed, --not-signed, --unpaid, --paid)
python epicevents.py contracts create
python epicevents.py contracts update
```

#### Events

```bash
python epicevents.py events list (options: --support-contact-id, --mine)
python epicevents.py events create
python epicevents.py events update
```

## 16. Roles and Permissions

### Management

* read all data
* create, update, and delete collaborators
* create and update contracts
* update events and filter them by support contact (option: --support-contact-id)
* assign a support collaborator to an event

### Sales

* read all data
* create clients
* update the clients they are responsible for
* update contracts related to their clients
* filter contracts by paid and unpaid contracts (option: --paid, --unpaid)
* filter contracts by signed and not signed contracts (option: --signed, --not-signed)
* create an event for a client with a signed contract

### Support

* read all data
* filter events by owned (option: --mine)
* update events assigned to them

## 17. Tests

### Run all tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=. --cov-report html
```

The project includes:

* unit tests
* integration tests
