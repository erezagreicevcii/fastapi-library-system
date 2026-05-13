from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, require_api_key

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("", response_model=list[schemas.AuthorRead])
def list_authors(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    return (
        db.query(models.Author)
        .order_by(models.Author.id)
        .offset(offset)
        .limit(page_size)
        .all()
    )


@router.get("/{author_id}", response_model=schemas.AuthorRead)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.get(models.Author, author_id)

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )

    return author


@router.post(
    "",
    response_model=schemas.AuthorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_author(
    author_in: schemas.AuthorCreate,
    db: Session = Depends(get_db),
):
    author = models.Author(**author_in.model_dump())
    db.add(author)
    db.commit()
    db.refresh(author)
    return author


@router.patch(
    "/{author_id}",
    response_model=schemas.AuthorRead,
    dependencies=[Depends(require_api_key)],
)
def update_author(
    author_id: int,
    author_in: schemas.AuthorUpdate,
    db: Session = Depends(get_db),
):
    author = db.get(models.Author, author_id)

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )

    update_data = author_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(author, field, value)

    db.commit()
    db.refresh(author)
    return author


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key)],
)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = db.get(models.Author, author_id)

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )

    db.delete(author)
    db.commit()
    return None
