from datetime import date, timedelta

from app.database import Base, SessionLocal, engine
from app import models


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    try:
        categories = [
            models.Category(name="Science Fiction"),
            models.Category(name="Fantasy"),
            models.Category(name="History"),
            models.Category(name="Technology"),
        ]
        db.add_all(categories)
        db.flush()

        authors = [
            models.Author(full_name="Ursula K. Le Guin", country="United States"),
            models.Author(full_name="Isaac Asimov", country="United States"),
            models.Author(full_name="Frank Herbert", country="United States"),
            models.Author(full_name="J. R. R. Tolkien", country="United Kingdom"),
            models.Author(full_name="Mary Beard", country="United Kingdom"),
            models.Author(full_name="Yuval Noah Harari", country="Israel"),
            models.Author(full_name="Robert C. Martin", country="United States"),
            models.Author(full_name="Martin Fowler", country="United Kingdom"),
            models.Author(full_name="Andrew Hunt", country="United States"),
            models.Author(full_name="David Thomas", country="United States"),
        ]
        db.add_all(authors)
        db.flush()

        books = [
            models.Book(title="The Left Hand of Darkness", isbn="9780441478125", category_id=categories[0].id, total_copies=3, published_year=1969, authors=[authors[0]]),
            models.Book(title="Foundation", isbn="9780553293357", category_id=categories[0].id, total_copies=4, published_year=1951, authors=[authors[1]]),
            models.Book(title="Dune", isbn="9780441172719", category_id=categories[0].id, total_copies=5, published_year=1965, authors=[authors[2]]),
            models.Book(title="The Hobbit", isbn="9780547928227", category_id=categories[1].id, total_copies=4, published_year=1937, authors=[authors[3]]),
            models.Book(title="The Fellowship of the Ring", isbn="9780547928210", category_id=categories[1].id, total_copies=3, published_year=1954, authors=[authors[3]]),
            models.Book(title="SPQR", isbn="9780871404237", category_id=categories[2].id, total_copies=3, published_year=2015, authors=[authors[4]]),
            models.Book(title="Sapiens", isbn="9780062316097", category_id=categories[2].id, total_copies=6, published_year=2011, authors=[authors[5]]),
            models.Book(title="Clean Code", isbn="9780132350884", category_id=categories[3].id, total_copies=4, published_year=2008, authors=[authors[6]]),
            models.Book(title="Refactoring", isbn="9780134757599", category_id=categories[3].id, total_copies=3, published_year=2018, authors=[authors[7]]),
            models.Book(title="The Pragmatic Programmer", isbn="9780201616224", category_id=categories[3].id, total_copies=5, published_year=1999, authors=[authors[8], authors[9]]),
            models.Book(title="Good Omens", isbn="9780060853983", category_id=categories[1].id, total_copies=2, published_year=1990, authors=[authors[0], authors[3]]),
            models.Book(title="Programming Patterns", isbn="9781234567001", category_id=categories[3].id, total_copies=2, published_year=2020, authors=[authors[7], authors[8]]),
            models.Book(title="Ancient Worlds", isbn="9781234567002", category_id=categories[2].id, total_copies=2, published_year=2012, authors=[authors[4], authors[5]]),
            models.Book(title="Robots and Empire", isbn="9780553299496", category_id=categories[0].id, total_copies=2, published_year=1985, authors=[authors[1]]),
            models.Book(title="Children of Dune", isbn="9780441104024", category_id=categories[0].id, total_copies=3, published_year=1976, authors=[authors[2]]),
            models.Book(title="The Silmarillion", isbn="9780544338012", category_id=categories[1].id, total_copies=2, published_year=1977, authors=[authors[3]]),
            models.Book(title="Roman Empire", isbn="9781234567003", category_id=categories[2].id, total_copies=2, published_year=2009, authors=[authors[4]]),
            models.Book(title="Homo Deus", isbn="9780062464316", category_id=categories[2].id, total_copies=3, published_year=2015, authors=[authors[5]]),
            models.Book(title="Agile Software Design", isbn="9781234567004", category_id=categories[3].id, total_copies=2, published_year=2017, authors=[authors[6], authors[7]]),
            models.Book(title="A Wizard of Earthsea", isbn="9780547722023", category_id=categories[1].id, total_copies=3, published_year=1968, authors=[authors[0]]),
        ]
        db.add_all(books)
        db.flush()

        members = [
            models.Member(full_name="Ariana Krasniqi", email="ariana@example.com", join_date=date(2025, 1, 10), is_active=True),
            models.Member(full_name="Blerim Gashi", email="blerim@example.com", join_date=date(2025, 2, 5), is_active=True),
            models.Member(full_name="Drita Berisha", email="drita@example.com", join_date=date(2025, 3, 12), is_active=True),
            models.Member(full_name="Elira Hoxha", email="elira@example.com", join_date=date(2025, 4, 20), is_active=True),
            models.Member(full_name="Fisnik Rama", email="fisnik@example.com", join_date=date(2025, 5, 9), is_active=True),
            models.Member(full_name="Gentiana Morina", email="gentiana@example.com", join_date=date(2025, 6, 2), is_active=True),
            models.Member(full_name="Ilir Deda", email="ilir@example.com", join_date=date(2025, 7, 15), is_active=True),
            models.Member(full_name="Jeta Shala", email="jeta@example.com", join_date=date(2025, 8, 1), is_active=True),
            models.Member(full_name="Kreshnik Aliu", email="kreshnik@example.com", join_date=date(2025, 9, 18), is_active=True),
            models.Member(full_name="Lira Mustafa", email="lira@example.com", join_date=date(2025, 10, 30), is_active=False),
        ]
        db.add_all(members)
        db.flush()

        today = date.today()

        loans = []
        for i in range(15):
            loans.append(
                models.Loan(
                    member_id=members[i % len(members)].id,
                    book_id=books[i % len(books)].id,
                    loan_date=today - timedelta(days=60 - i),
                    due_date=today - timedelta(days=45 - i),
                    return_date=today - timedelta(days=35 - i),
                )
            )

        for i in range(8):
            loans.append(
                models.Loan(
                    member_id=members[i % 9].id,
                    book_id=books[(i + 5) % len(books)].id,
                    loan_date=today - timedelta(days=7 + i),
                    due_date=today + timedelta(days=14 - i),
                    return_date=None,
                )
            )

        for i in range(7):
            loans.append(
                models.Loan(
                    member_id=members[i % 9].id,
                    book_id=books[(i + 10) % len(books)].id,
                    loan_date=today - timedelta(days=30 + i),
                    due_date=today - timedelta(days=5 + i),
                    return_date=None,
                )
            )

        db.add_all(loans)
        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    reset_database()
    seed()
    print("Database seeded successfully.")
