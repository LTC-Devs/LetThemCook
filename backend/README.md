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

### Local database 
Quick start:
```sh
docker compose -f ../compose.yaml up database -d
```

Database connection is configured under `DATABASES` in [server settings](config/settings.py).

#### Database connection
The connection details for the database are stored in the .env file, which python on its own does not read by default.
For uv add the flag `--env-file .env` to every run command, e.g. `uv run --env-file .env python manage.py runserver`
For pip: *instructions left as an exercise for the reader*
Set up the .env file with:
```sh
cp template.env .env
```

Populate the database with sample product names using [this script](products/management/commands/seed_products.py):
```sh
python manage.py migrate # initialize schema
python manage.py seed_products
```

## Running the server
```sh
python manage.py runserver
```

## Endpoints

### EAN product lookup
- **Route**: `GET .../lookup/?ean=<barcode>`
-  **Description**: Takes a product barcode (EAN), fetches product metadata from the external OpenFoodFacts API, and searches the local database for matching products using fuzzy name matching (`TrigramSearch`).
    - **NOTE**: Open Food Facts lookup API has rate limits of 15 requests/min, avoid spamming the API and preferably setup contact info (e.g. email) in env variable `USER_CONTACT`; it is used in `User-Agent` header for identification ([See their API docs](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/#authentication))

#### Responses
- `200 OK`: Returns JSON with the ean, raw upstream_data, and a list of up to 5 local matches (id, data).
- `400 Bad Request`: EAN is missing, non-digit, or not between 8 and 14 characters.
- `404 Not Found`: EAN was not found in OpenFoodFacts.
- `502 Bad Gateway`: OpenFoodFacts API request failed or timed out.

#### Example response
```json
{
  "ean": "5900820000042",
  "upstream_data": {
    "product_name": "Mleko UHT 2%",
    "product_name_pl": "Łaciate UHT 2%",
    "generic_name_pl": "Mleko",
    "generic_name": "",
    "brands": "Mlekpol, Łaciate",
    "pnns_groups_2": "Milk and yogurt",
    "categories_tags": [
      "en:dairies",
      "en:milks-liquid-and-powder",
      "en:milks",
       ...
    ]
  },
  "matches": [
    {
      "id": 1,
      "data": "Mleko chude"
    },
    {
      "id": 6,
      "data": "Mleko bez laktozy"
    }
  ]
}
```

## LTC database (Django ORM)

The models for recipes, users, pantry, recommendations and shopping are in their
respective Django apps. Recipe JSON has not been imported.

See [docs/DATABASE.md](../docs/DATABASE.md) for schema and setup.

## Monorepo note

This README belongs to `backend/`. Start PostgreSQL **from repository root** with
`docker compose -f database/compose.yml up -d`, then run the Django commands
**from `backend/`** (`uv sync`, `uv run python manage.py migrate`, and so on).
For current paths and the complete setup, see [`../README.md`](../README.md).
