# LTC — current project architecture - 25.10.2026

```text
frontend/           React/Next.js web client (not yet integrated)
   │ HTTP/JSON
   ▼
backend/            Django and application business logic
   ├── config/      Django settings / URLs
   ├── products/    Products / EAN lookup
   ├── recipes/     Cookbook, recipe and ingredient ORM
   ├── pantry/      Pantry ORM
   ├── users/       User preferences ORM
   ├── recommendations/   Recommendations ORM / DB adapter
   ├── recommender_prototype/ Independent scoring algorithm
   └── shopping/    Shopping list ORM
   │ SQL via Django ORM
   
database/           PostgreSQL started via Docker Compose
```