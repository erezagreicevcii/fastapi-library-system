from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, require_api_key

router = APIRouter(prefix="/loans", tags=["loans"])


def count_active_loans_for_book(db: Session, book_id: int) -> int:
    return (
        db.query(models.Loan)
        .filter(
            models.Loan.book_id == book_id,
            models.Loan.return_date.is_(None),
        )
        .count()
    )


@router.post(
    "",
    response_model=schemas.LoanRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_loan(loan_in: schemas.LoanCreate, db: Session = Depends(get_db)):
    member = db.get(models.Member, loan_in.member_id)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    if not member.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive members cannot borrow books",
        )

    book = db.get(models.Book, loan_in.book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    active_loans_count = count_active_loans_for_book(db, loan_in.book_id)

    if book.total_copies <= active_loans_count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No copies available",
        )

    loan = models.Loan(
        member_id=loan_in.member_id,
        book_id=loan_in.book_id,
        loan_date=date.today(),
        due_date=loan_in.due_date,
        return_date=None,
    )

    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@router.post(
    "/{loan_id}/return",
    response_model=schemas.LoanRead,
    dependencies=[Depends(require_api_key)],
)
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.get(models.Loan, loan_id)

    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )

    if loan.return_date is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Loan already returned",
        )

    loan.return_date = date.today()

    db.commit()
    db.refresh(loan)
    return loan


@router.get("", response_model=schemas.PaginatedLoans)
def list_loans(
    member_id: int | None = None,
    book_id: int | None = None,
    status_filter: str | None = Query(
        default=None,
        alias="status",
        pattern="^(active|returned|overdue)$",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Loan)

    if member_id is not None:
        query = query.filter(models.Loan.member_id == member_id)

    if book_id is not None:
        query = query.filter(models.Loan.book_id == book_id)

    today = date.today()

    if status_filter == "active":
        query = query.filter(models.Loan.return_date.is_(None))
    elif status_filter == "returned":
        query = query.filter(models.Loan.return_date.is_not(None))
    elif status_filter == "overdue":
        query = query.filter(
            models.Loan.return_date.is_(None),
            models.Loan.due_date < today,
        )

    total = query.count()
    offset = (page - 1) * page_size

    loans = (
        query.order_by(models.Loan.loan_date.desc(), models.Loan.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return schemas.PaginatedLoans(
        items=loans,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=schemas.calculate_total_pages(total, page_size),
    )
