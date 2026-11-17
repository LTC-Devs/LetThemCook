# LTC — Django ↔ Next.js (pierwsza integracja)

Ta zmiana dodaje publiczne, **tylko do odczytu** API przepisów oraz widok listy i szczegółów w Next.js.

## Endpoints

- `GET /api/recipes/` — publiczne przepisy (paginacja po 20), `?q=szukany+tytul&page=2`
- `GET /api/recipes/<id>/` — szczegóły publicznego przepisu
- `GET /api/products/lookup/?ean=...` — dotychczasowy endpoint, bez zmian

**Prywatne przepisy użytkowników nie są zwracane przez te endpointy.** To nie zastępuje mechanizmu uwierzytelniania. Import JSON, CRUD przepisów, spiżarnia i rekomendacje przez API są na później.

## Lokalny start (z katalogu App/)

Trzy terminale:

```bash
# Terminal 1: PostgreSQL (już działający kontener można pozostawić)
docker compose -f database/compose.yml up -d

# Terminal 2: Django
cd backend
uv run python manage.py check
uv run python manage.py runserver 127.0.0.1:8000

# Terminal 3: Next.js
cd frontend
npm run dev
```

Otwórz `http://127.0.0.1:8000/api/recipes/` — oczekiwany JSON z `results` i `count`.
Otwórz `http://localhost:3000/recipes` — lista z Django. Jeśli `results: []`, połączenie może działać poprawnie: baza nie ma jeszcze zaimportowanych przepisów. Możesz dodać testowy rekord przez Django Admin.

Next.js wykonuje żądania na **serwerze**, dlatego nie wymaga tu CORS. Opcjonalny plik `frontend/.env.local` z `DJANGO_API_BASE_URL=http://127.0.0.1:8000` jest ignorowany przez Git. Po zmianie env uruchom ponownie Next.js.

## Testy

```bash
cd backend
uv run python manage.py test recipes
uv run python manage.py check

cd ../frontend
npm run lint
npm run build
```

Jeśli `npm run lint` nie istnieje w `package.json`, użyj `npx eslint .`.

## Środowisko produkcyjne

`127.0.0.1` jest wyłącznie na potrzeby lokalnego uruchamiania. W produkcji podaj adres Django dostępny z serwera Next.js przez zmienną `DJANGO_API_BASE_URL` (bez `NEXT_PUBLIC_`). Dodanie POST/PUT/DELETE, cookies/sesji, uprawnień i ochrony CSRF wymaga osobnego etapu integracji.
