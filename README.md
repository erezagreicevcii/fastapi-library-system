# FastAPI Library System

A backend API for a small library lending system. The API allows users to manage books, authors, categories, members, and loans. It includes book search with filters, pagination, loan reports, API key protection for write operations, seed data, tests, and Alembic database migrations.

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Set the API key:
```bash
$env:LIBRARY_API_KEY="dev-secret-key"
```

Apply database migrations:
```bash
alembic upgrade head
```

Seed the database:

```bash
python -m scripts.seed
```

Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
```bash
http://127.0.0.1:8005
```

Interactive API docs:
```bash
http://127.0.0.1:8005/docs
```

## Docker
Run the app with Docker Compose:
```bash
docker compose up --build
```

The API will be available at:
```bash
http://localhost:8005
```

## Tests
Run tests with:
```bash
python -m pytest
```

## API Key
All `POST`, `PATCH`, and `DELETE` endpoints require this request header:
```bash
X-API-Key: dev-secret-key
```

The expected value is read from the `LIBRARY_API_KEY` environment variable.

## Endpoints
Health:
```bash
GET /api/v1/health
```
Categories:
```bash
GET /api/v1/categories
GET /api/v1/categories/{id}
POST /api/v1/categories
PATCH /api/v1/categories/{id}
DELETE /api/v1/categories/{id}
```


Authors:
```bash
GET /api/v1/authors
GET /api/v1/authors/{id}
POST /api/v1/authors
PATCH /api/v1/authors/{id}
DELETE /api/v1/authors/{id}
```

Members:
```bash
GET /api/v1/members
GET /api/v1/members/{id}
POST /api/v1/members
PATCH /api/v1/members/{id}
DELETE /api/v1/members/{id}
```

Books:
```bash
GET /api/v1/books
GET /api/v1/books/{id}
POST /api/v1/books
PATCH /api/v1/books/{id}
DELETE /api/v1/books/{id}
GET /api/v1/books/search
GET /api/v1/books/{id}/loan-history
```

Loans:
```bash
GET /api/v1/loans
POST /api/v1/loans
POST /api/v1/loans/{id}/return
```

Reports:
```bash
GET /api/v1/reports/top-borrowers
GET /api/v1/reports/overdue-loans
```

## Notes
lighthouse

Known limitations:

- Docker support is included, but local SQLite development is the main tested setup.
- The project uses a simple API key auth system, not user login or OAuth.
- More tests could be added for every CRUD endpoint if there was more time.





