# Library Management App

A Python library management learning project. The CLI currently uses JSON
storage, and MySQL integration is under development.

## Prepare the environment

From the `school-projects` directory:

```bash
cd library_management_app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `library_management_app/.env` with your local MySQL settings:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=library
DB_USER=library_user
DB_PASSWORD=your_password_here
```

Use a local database and user that you have created. Keep `.env` out of Git;
the repository already ignores it. Existing environment variables take
precedence over values in `.env`.

The connection module loads `.env` from the application directory regardless
of the current working directory. Importing the repository does not connect
to MySQL. A connection is opened only when requested. Missing required
settings raise `RuntimeError` listing the missing variable names.

## Run the CLI

From `library_management_app` with the virtual environment activated:

```bash
python -m cli.main
```

## Run tests

Install pytest in the same virtual environment, then run the tests from
`library_management_app`:

```bash
python -m pip install pytest
python -m pytest tests/ -v
```

The import and configuration tests do not require a MySQL server. Real MySQL
integration tests are skipped unless `LIBRARY_TEST_MYSQL=1` is set.
