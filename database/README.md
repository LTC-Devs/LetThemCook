# PostgreSQL database (local development)

This folder contains PostgreSQL *infrastructure*. Django's tables are defined
by `backend/*/models.py` and versioned by `backend/*/migrations/`.

From the **repository root**:

```bash
docker compose -f database/compose.yml up -d
cd backend
uv run python manage.py migrate
uv run python manage.py test
```

The Compose file uses local test credentials (`user` / `example`, DB `test_db`,
port 5432). **Do not use these credentials for deployment.** At present the
Django database settings use the same local development values.

The existing container is named `postgres-test`. The Compose project name is
explicitly preserved to avoid creating a competing project after moving the file.
Do not delete/recreate your existing container or run `down -v` just for this
folder reorganisation, because data stored inside the original container may
be lost if it is replaced.

To inspect tables without a host `psql` installation:

```bash
docker exec -it postgres-test psql -U user -d test_db
# inside psql: \dt
# leave psql: \q
```

More details: [`docs/DATABASE.md`](../docs/DATABASE.md).
