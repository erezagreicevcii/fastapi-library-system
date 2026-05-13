from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, require_api_key

# Create a router to group all category-related endpoints
# All routes in this file will automatically start with /categories
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[schemas.CategoryRead])
def list_categories(
    # Pagination parameters: prevents loading thousands of rows at once
    page: int = Query(default=1, ge=1), # Current page, must be >= 1
    page_size: int = Query(default=20, ge=1, le=100), # Items per page (max 100)
    db: Session = Depends(get_db), # Database session dependency
):
    """Fetch a paginated list of all categories."""
    offset = (page - 1) * page_size # Calculate how many rows to skip
    return (
        db.query(models.Category)
        .order_by(models.Category.id) # Keep results sorted by ID
        .offset(offset) # Skip the results from previous pages
        .limit(page_size) # Return only the requested number of items
        .all()
    )


@router.get("/{category_id}", response_model=schemas.CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Retrieve details of a specific category by its ID."""
    category = db.get(models.Category, category_id)

    # If the ID doesn't exist in the database, return a 404 error
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


@router.post(
    "",
    response_model=schemas.CategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)], # Security: API Key required for creation
)
def create_category(
    category_in: schemas.CategoryCreate,
    db: Session = Depends(get_db),
):
    """Create a new category in the database."""
    # Convert incoming Pydantic data into a SQLAlchemy database model
    category = models.Category(**category_in.model_dump())
    db.add(category)

    try:
        db.commit() # Attempt to save changes to the database
    except IntegrityError:
        # If the category name already exists (Unique Constraint), return 409
        db.rollback() # Undo the failed action
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already exists",
        )

    db.refresh(category) # Get the newly generated ID from the database
    return category


@router.patch(
    "/{category_id}",
    response_model=schemas.CategoryRead,
    dependencies=[Depends(require_api_key)], # Security: API Key required for modification
)
def update_category(
    category_id: int,
    category_in: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
):
    """Partially update an existing category (only fields sent in the request)."""
    category = db.get(models.Category, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    # model_dump(exclude_unset=True) ensures we only update fields the user actually sent
    update_data = category_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(category, field, value) # Apply changes to the database object

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already exists",
        )

    db.refresh(category)
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT, # 204 means "Success, but no content to return"
    dependencies=[Depends(require_api_key)], # Security: API Key required for deletion
)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Permanently delete a category from the system."""
    category = db.get(models.Category, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    db.delete(category)
    db.commit() # Confirm the deletion in the database
    return None # Return nothing because the object is gone