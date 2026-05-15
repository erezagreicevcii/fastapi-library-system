# Reasoning

## Database Choice

I used SQLite for local development because it is simple to run, does not require a separate database server, and works well for this assessment. The application is structured so it can also be run with Postgres through Docker Compose.

## Many-to-Many Relationship

Books and authors have a many-to-many relationship because one book can have multiple authors, and one author can write multiple books. I modelled this using a `book_authors` association table with a composite primary key of `book_id` and `author_id`. This avoids duplicated author data and keeps the relationship normalized.

## Search Endpoint and N+1 Avoidance

The book search endpoint uses SQLAlchemy joins and eager loading with `joinedload` for category and authors. This means the API does not query authors separately for every book result. The filters are applied to one query before pagination, and a separate count is used to calculate `total` and `total_pages`.

## Delete Conflicts

Deleting a member or book with active loans returns `409 Conflict` because the request conflicts with the current state of the system. A member who still has borrowed books, or a book that is currently borrowed, should not be removed because that would break the lending history and active loan data.

## Test Suite

I tested the loan flow because it contains the most important business rules: borrowing, returning, no available copies, inactive members, and returning an already returned loan. I also tested the book search endpoint because it combines filters, sorting, pagination, and availability logic. I skipped exhaustive CRUD tests for every resource due to time, but the main business logic is covered.

## Scope Choices

Completed:
- SQLAlchemy schema for members, authors, categories, books, book_authors, and loans
- CRUD endpoints for books, members, authors, and categories
- Loan borrow, return, and filtered list endpoints
- Book search with composed filters, sorting, availability, and pagination
- Reports using joins
- Seed data
- API key protection for write endpoints
- Pytest tests for loan and search behaviour
- Alembic initial migration

Cut or limited:
- Full user authentication was not implemented because the requirement only asked for API key auth.
- CRUD tests for every resource were not added due to time.
- The Docker setup is kept simple.

## External Resources Used

- Udemy Course: "FastAPI - The Complete Course 2026 (Beginner + Advanced)"
- YouTube: How to build a FastAPI app with PostgreSQL: https://youtu.be/398DuQbQJq0
- Youtube: Python API Development - Comprehensive Course for Beginners: https://youtu.be/0sOvCWFmrtA
- FastAPI documentation: https://fastapi.tiangolo.com/
- SQLAlchemy documentation: https://docs.sqlalchemy.org/
- Pydantic documentation: https://docs.pydantic.dev/
- Alembic documentation: https://alembic.sqlalchemy.org/
- Pytest documentation: https://docs.pytest.org/
- AI assistance: used for step-by-step guidance, debugging, and project structure suggestions.