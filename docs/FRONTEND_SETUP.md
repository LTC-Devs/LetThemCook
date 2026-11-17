# Frontend — architecture and next steps

The Next.js + React + TypeScript + Tailwind scaffold is located at [`../frontend/`](../frontend/).
It is independent of Django and PostgreSQL and communicates with them **only via the Django API**.
There is no direct browser-to-PostgreSQL connection.

## Development

In two terminals (from repository root):

```bash
# Terminal A (backend):
docker compose -f database/compose.yml up -d
cd backend && uv run python manage.py runserver

# Terminal B (frontend):
cd frontend && npm ci && npm run dev
```

App URLs: frontend http://localhost:3000; Django http://127.0.0.1:8000.

## Current scope

This commit only prepares routes, components and project tooling. Views contain example
text but do **not** call the backend. Authentication, REST endpoints, CORS/proxy strategy,
real recipes and functional UI will be implemented in separate changes.

## Suggested next work

1. Agree on Django REST endpoint contracts and serializers (`recipes`, `pantry`, etc.).
2. Choose session/authentication + local development CORS/proxy approach.
3. Implement recipe list + detail against real API responses.
4. Add pantry, recommendations, shopping, user settings.
