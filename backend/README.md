# Product search service

## Setup
Python version: 3.12

### pip
```sh
cd backend/
python -m venv .venv
pip install .
```

### uv
```sh
cd backend/
uv sync  
```

### Local database (for tests)
Quick start:
add environment variables from [env template](template.env), then run:
```sh
docker compose -f test-db/compose.yaml up database -d
```

#### Database connection
The connection details for the database are stored in the .env file, which python on its own does not read by default.
For uv add the flag `--env-file .env` to every run command, e.g. `uv run --env-file .env python manage.py runserver`
For pip: *instructions left as an exercise for the reader*
Set up the .env file with:
```sh
cp template.env .env
```

## Updating db
with current migrations
```sh
python manage.py migrate
```

## Running the server
```sh
python manage.py runserver
```

## Endpoints
**TODO** - require updating with new models

## Admin panel access
Aby wejść do panelu administratora Django (Django Admin):

Make sure migrations are applied
```powershell
python manage.py migrate
```

Create superuser account (if it is not present)
```
python manage.py createsuperuser
```
Email can be left empty.

Run dev server
```
python manage.py runserver
```

Open the admin panel in browser:
-> **[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)** *(or `http://localhost:8000/admin/`)*

Log in with superuser credentials from step 2.

## LTC database (Django ORM)

The models for recipes, users, pantry, recommendations and shopping are in their
respective Django apps. Data import to be implemented.

See [docs/DATABASE.md](../docs/DATABASE.md) for schema and setup.

## Monorepo note

This README belongs to `backend/`. Start test PostgreSQL `docker compose -f test-db/compose.yml up -d`, then run the Django commands
**in `backend/`** (`uv sync`, `uv run python manage.py migrate`, and so on).
For current paths and the complete setup, see [`../README.md`](../README.md).
