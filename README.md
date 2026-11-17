# App
Main repository for the app's code

## LTC monorepo

- `backend/` — Django, ORM, migrations recommendations algorithms
- `frontend/` — frontend React/Next.js
- `docs/` — documentation, including database schemas

## Run locally

```sh
cp template.env .env
docker compose up --build -d
```
Frontend will be available at <http://localhost:3000>, the backend admin panel is at <http://localhost:8000/admin>.


Backend details: [`backend/README.md`](backend/README.md).
Frontend details: [`frontend/README.md`](frontend/README.md).
