from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/top-borrowers", response_model=list[schemas.TopBorrower])
def get_top_borrowers(
    limit: int = Query(default=5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(models.Member, func.count(models.Loan.id).label("total_loans"))
        .join(models.Loan, models.Member.id == models.Loan.member_id)
        .group_by(models.Member.id)
        .order_by(func.count(models.Loan.id).desc(), models.Member.id)
        .limit(limit)
        .all()
    )

    return [
        schemas.TopBorrower(member=member, total_loans=total_loans)
        for member, total_loans in rows
    ]


@router.get("/overdue-loans", response_model=list[schemas.OverdueLoanReport])
def get_overdue_loans(db: Session = Depends(get_db)):
    today = date.today()

    rows = (
        db.query(
            models.Loan.id.label("loan_id"),
            models.Member.full_name.label("member_name"),
            models.Book.title.label("book_title"),
            models.Loan.due_date.label("due_date"),
        )
        .join(models.Member, models.Loan.member_id == models.Member.id)
        .join(models.Book, models.Loan.book_id == models.Book.id)
        .filter(
            models.Loan.return_date.is_(None),
            models.Loan.due_date < today,
        )
        .order_by(models.Loan.due_date.asc())
        .all()
    )

    return [
        schemas.OverdueLoanReport(
            loan_id=row.loan_id,
            member_name=row.member_name,
            book_title=row.book_title,
            due_date=row.due_date,
            days_overdue=(today - row.due_date).days,
        )
        for row in rows
    ]
