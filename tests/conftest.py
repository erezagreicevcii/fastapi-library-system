import os
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app import models



SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    os.environ["LIBRARY_API_KEY"] = "test-key"
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers():
    return {"X-API-Key": "test-key"}


@pytest.fixture()
def sample_data(db_session):
    category = models.Category(name="Technology")
    author = models.Author(full_name="Robert C. Martin", country="United States")
    member = models.Member(
        full_name="Test Member",
        email="member@example.com",
        join_date=date(2026, 1, 1),
        is_active=True,
    )
    inactive_member = models.Member(
        full_name="Inactive Member",
        email="inactive@example.com",
        join_date=date(2026, 1, 1),
        is_active=False,
    )

    book = models.Book(
        title="Clean Code",
        isbn="9780132350884",
        category=category,
        total_copies=1,
        published_year=2008,
        authors=[author],
    )

    second_book = models.Book(
        title="Refactoring",
        isbn="9780134757599",
        category=category,
        total_copies=2,
        published_year=2018,
        authors=[author],
    )

    db_session.add_all([category, author, member, inactive_member, book, second_book])
    db_session.commit()

    return {
        "category": category,
        "author": author,
        "member": member,
        "inactive_member": inactive_member,
        "book": book,
        "second_book": second_book,
    }
