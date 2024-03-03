# HappyFox Interview Project

## Introduction
This project is part of the HappyFox interview process. It includes functionality to fetch and process emails based on certain rules, using Python and the Gmail API.

## Folder Structure

```
happyfox/
│
├── alembic/                  # Alembic migration scripts and settings
│   ├── env.py                # Alembic environment configuration
│   ├── script.py.mako        # Alembic script template
│   └── versions/             # Alembic migration versions
│
├── db/                       # Database models and engine setup
│   ├── __init__.py
│   ├── engine.py             # SQLAlchemy database engine setup
│   └── models.py             # SQLAlchemy database models
│
├── rule_processor/           # Rule processing logic
│   ├── __init__.py
│   ├── constants.py          # Rule processor constants
│   ├── rule_processor.py     # Main rule processing module
│   └── rules.json            # JSON file with rules for processing emails
│
├── docs/                         # Documentation files
│   ├── HappyFox_Backend_Assignment.pdf
│   ├── HappyFox_Interview_Task_FR_NFR.pdf
│   └── Setting_Up_OAuth_for_Gmail_and_Obtaining_Credentials.pdf
│
├── alembic.ini               # Alembic configuration file
├── constants.py              # Global constants
├── credentials.json          # Gmail API credentials (ignore)
├── docker-compose.yml        # Docker Compose file for running PostgreSQL
├── fetch_email.py            # Script to fetch emails
├── process_email.py          # Script to process emails
├── pyproject.toml            # Poetry project file
├── poetry.lock               # Poetry lock file (dependencies)
└── token.pickle              # Gmail API token (ignore)
```

## Prerequisites
- Python 3.10
- Poetry for Python dependency management
- Gmail API credentials in `credentials.json`
- Docker and Docker Compose for running the PostgreSQL database
- Virtual Env for this project setup

## Setup and Installation

### Installing Dependencies
1. Install Poetry:
   Follow the instructions at [Poetry Installation](https://python-poetry.org/docs/#installation).
2. Install project dependencies:
   ```bash
   poetry install
   ```

### Database Setup with Docker Compose
1. Ensure Docker is installed and running.
2. Use Docker Compose to start a PostgreSQL instance:
   ```bash
   docker-compose up -d
   ```
3. Update the `DATABASE_URL` in `alembic.ini` and `db/engine.py` to point to your Dockerized PostgreSQL instance.
4. Run Alembic migrations to set up the database schema:
   ```bash
   poetry run alembic upgrade head
   ```

### Gmail API Setup
1. Place your `credentials.json` file from the Google Developers Console in the project root.
2. The first run will open a browser to authenticate and generate `token.pickle`.

## Running the Application
To fetch and process emails:
```bash
python fetch_email.py
python process_email.py
```

## Testing
- Unit tests can be added in a `tests/` directory.
- Use `pytest` to run tests:
  ```bash
  coverage run -m unittest discover -s tests
  ```

## Note on Production Readiness
This project was developed as part of an interview task. While the code has been written with production setup and best practices in mind, it is not intended for deployment in a production environment as-is. This codebase serves as a demonstration of coding standards, design patterns, and practices suitable for a production-level application, but further testing, development, and security considerations are required before actual production use.


## License
MIT 

