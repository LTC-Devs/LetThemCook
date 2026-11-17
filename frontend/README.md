# Let Them Cook — Frontend

Next.js (React, TypeScript, App Router, Tailwind CSS, ESLint) scaffold.
Pages are **placeholders only**: no Django API integration and no authentication yet.

## Run locally

Prerequisites: Node.js 20.9+, npm and Docker.

1. Run the backend
```sh
docker compose -f ../compose.yaml up backend -d
```
2. Start the frontend
```bash
cp template.env .env
npm ci
npm run dev
```

Visit http://localhost:3000. For production checks, run `npm run lint` and `npm run build`.

## Directory layout

- `src/app/` — App Router pages (`recipes`, `pantry`, `recommendations`, `shopping`, `profile`)
- `src/components/layout/` — shared navigation / layout components
- `src/components/ui/` — reusable UI primitives
- `src/components/recipes/`, `pantry/`, `shopping/` — feature-specific components
- `src/lib/` — future Django API client and shared helpers
- `src/types/` — API contract / frontend types
- `src/hooks/` — custom React hooks (as needed)
