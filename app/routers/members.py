from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app import models, schemas
from app.dependencies import get_db, require_api_key

# Router for managing library members
router = APIRouter(prefix="/members", tags=["members"])

@router.get("", response_model=list[schemas.MemberRead])
def list_members(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    #list all members with basic pagination
    offset = (page - 1) * page_size
    return (
        db.query(models.Member)
        .order_by(models.Member.id)
        .offset(offset)
        .limit(page_size)
        .all()
    )

@router.get("/{member_id}", response_model=schemas.MemberRead)
def get_member(member_id: int, db: Session = Depends(get_db)):
    #Retrieve profile details for a specific member
    member = db.get(models.Member, member_id)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    return member

@router.post(
    "",
    response_model=schemas.MemberRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_member(
    member_in: schemas.MemberCreate,
    db: Session = Depends(get_db),
):
    #Register a new member in the system
    member = models.Member(**member_in.model_dump())
    db.add(member)

    try:
        db.commit()
    except IntegrityError:
        # Prevents duplicate emails in the system
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Member email already exists",
        )

    db.refresh(member)
    return member

@router.patch(
    "/{member_id}",
    response_model=schemas.MemberRead,
    dependencies=[Depends(require_api_key)],
)
def update_member(
    member_id: int,
    member_in: schemas.MemberUpdate,
    db: Session = Depends(get_db),
):
    #Update member contact info or status
    member = db.get(models.Member, member_id)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    update_data = member_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(member, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Member email already exists",
        )

    db.refresh(member)
    return member

@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key)],
)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """
    Delete a member only if they have no active loans.
    Business Rule: Return 409 Conflict if they still have books to return.
    """
    member = db.get(models.Member, member_id)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    # Check for active loans (where return_date is null)
    active_loans_count = (
        db.query(models.Loan)
        .filter(
            models.Loan.member_id == member_id,
            models.Loan.return_date.is_(None),
        )
        .count()
    )

    if active_loans_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete member with active loans",
        )

    db.delete(member)
    db.commit()
    return None