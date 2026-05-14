from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.dependencies import get_db, require_api_key

router = APIRouter(prefix="/books", tags=["books"])


def get_authors_by_ids(db: Session, author_ids: list[int]) -> list[models.Author]:
    if not author_ids:
        return []

    authors = db.query(models.Author).filter(models.Author.id.in_(author_ids)).all()

    if len(authors) != len(set(author_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more authors were not found",
        )

    return authors


@router.get("", response_model=list[schemas.BookRead])
def list_books(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size

    return (
        db.query(models.Book)
        .options(joinedload(models.Book.category), joinedload(models.Book.authors))
        .order_by(models.Book.id)
        .offset(offset)
        .limit(page_size)
        .all()
    )


@router.get("/search", response_model=schemas.PaginatedBooks)
def search_books(
    q: str | None = None,
    category_id: int | None = None,
    author_id: int | None = None,
    available_only: bool = False,
    published_after: int | None = None,
    published_before: int | None = None,
    sort_by: str = Query(default="title", pattern="^(title|published_year|popularity)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    active_loans_subquery = (
        db.query(
            models.Loan.book_id.label("book_id"),
            func.count(models.Loan.id).label("active_loans"),
        )
        .filter(models.Loan.return_date.is_(None))
        .group_by(models.Loan.book_id)
        .subquery()
    )

    popularity_subquery = (
        db.query(
            models.Loan.book_id.label("book_id"),
            func.count(models.Loan.id).label("total_loans"),
        )
        .group_by(models.Loan.book_id)
        .subquery()
    )

    query = (
        db.query(models.Book)
        .options(joinedload(models.Book.category), joinedload(models.Book.authors))
        .outerjoin(active_loans_subquery, models.Book.id == active_loans_subquery.c.book_id)
        .outerjoin(popularity_subquery, models.Book.id == popularity_subquery.c.book_id)
    )

    if q:
        query = query.filter(models.Book.title.ilike(f"%{q}%"))

    if category_id is not None:
        query = query.filter(models.Book.category_id == category_id)

    if author_id is not None:
        query = query.join(models.Book.authors).filter(models.Author.id == author_id)

    if available_only:
        active_loans_count = func.coalesce(active_loans_subquery.c.active_loans, 0)
        query = query.filter(models.Book.total_copies > active_loans_count)

    if published_after is not None:
        query = query.filter(models.Book.published_year > published_after)

    if published_before is not None:
        query = query.filter(models.Book.published_year < published_before)

    total = query.distinct().count()

    if sort_by == "title":
        sort_column = models.Book.title
    elif sort_by == "published_year":
        sort_column = models.Book.published_year
    else:
        sort_column = func.coalesce(popularity_subquery.c.total_loans, 0)

    if sort_order == "desc":
        query = query.order_by(desc(sort_column), models.Book.id)
    else:
        query = query.order_by(asc(sort_column), models.Book.id)

    offset = (page - 1) * page_size

    books = (
        query.distinct()
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return schemas.PaginatedBooks(
        items=books,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=schemas.calculate_total_pages(total, page_size),
    )


@router.get("/{book_id}", response_model=schemas.BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = (
        db.query(models.Book)
        .options(joinedload(models.Book.category), joinedload(models.Book.authors))
        .filter(models.Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return book


@router.post(
    "",
    response_model=schemas.BookRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_book(book_in: schemas.BookCreate, db: Session = Depends(get_db)):
    category = db.get(models.Category, book_in.category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    authors = get_authors_by_ids(db, book_in.author_ids)

    data = book_in.model_dump(exclude={"author_ids"})
    book = models.Book(**data)
    book.authors = authors

    db.add(book)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book ISBN already exists",
        )

    db.refresh(book)
    return book


@router.patch(
    "/{book_id}",
    response_model=schemas.BookRead,
    dependencies=[Depends(require_api_key)],
)
def update_book(
    book_id: int,
    book_in: schemas.BookUpdate,
    db: Session = Depends(get_db),
):
    book = (
        db.query(models.Book)
        .options(joinedload(models.Book.category), joinedload(models.Book.authors))
        .filter(models.Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    update_data = book_in.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category = db.get(models.Category, update_data["category_id"])
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

    if "author_ids" in update_data:
        book.authors = get_authors_by_ids(db, update_data.pop("author_ids"))

    for field, value in update_data.items():
        setattr(book, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book ISBN already exists",
        )

    db.refresh(book)
    return book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key)],
)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    active_loans_count = (
        db.query(models.Loan)
        .filter(
            models.Loan.book_id == book_id,
            models.Loan.return_date.is_(None),
        )
        .count()
    )

    if active_loans_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete book with active loans",
        )

    db.delete(book)
    db.commit()
    return None


@router.get("/{book_id}/loan-history", response_model=schemas.PaginatedBookLoanHistory)
def get_book_loan_history(
    book_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    book = db.get(models.Book, book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    query = (
        db.query(models.Loan, models.Member.full_name.label("member_name"))
        .join(models.Member, models.Loan.member_id == models.Member.id)
        .filter(models.Loan.book_id == book_id)
        .order_by(models.Loan.loan_date.desc(), models.Loan.id.desc())
    )

    total = query.count()
    offset = (page - 1) * page_size

    rows = query.offset(offset).limit(page_size).all()

    items = [
        schemas.BookLoanHistoryItem(
            id=loan.id,
            member_id=loan.member_id,
            member_name=member_name,
            loan_date=loan.loan_date,
            due_date=loan.due_date,
            return_date=loan.return_date,
        )
        for loan, member_name in rows
    ]

    return schemas.PaginatedBookLoanHistory(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=schemas.calculate_total_pages(total, page_size),
    )
