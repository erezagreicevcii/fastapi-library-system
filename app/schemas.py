from datetime import date
from math import ceil
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Common response for errors
class ErrorResponse(BaseModel):
    detail: str

# AUTHOR SCHEMAS 
class AuthorBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    country: str | None = Field(default=None, max_length=100)

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, max_length=100)

class AuthorRead(AuthorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# CATEGORY SCHEMAS 
class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)

class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# MEMBER SCHEMAS 
class MemberBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    join_date: date
    is_active: bool = True

class MemberCreate(MemberBase):
    pass

class MemberUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    join_date: date | None = None
    is_active: bool | None = None

class MemberRead(MemberBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# BOOK SCHEMAS
class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    isbn: str = Field(min_length=1, max_length=30)
    category_id: int
    total_copies: int = Field(ge=0)
    published_year: int | None = None

class BookCreate(BookBase):
    # Field to send list of authors when creating a book
    author_ids: list[int] = Field(default_factory=list)

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    isbn: str | None = Field(default=None, min_length=1, max_length=30)
    category_id: int | None = None
    total_copies: int | None = Field(default=None, ge=0)
    published_year: int | None = None
    author_ids: list[int] | None = None

class BookRead(BookBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: CategoryRead
    authors: list[AuthorRead] = []

# LOAN SCHEMAS 
class LoanBase(BaseModel):
    member_id: int
    book_id: int
    due_date: date

class LoanCreate(LoanBase):
    pass

class LoanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    member_id: int
    book_id: int
    loan_date: date
    due_date: date
    return_date: date | None = None

# Combined schema for details
class LoanWithDetails(LoanRead):
    member: MemberRead
    book: BookRead

# PAGINATION & REPORTS 
class PaginatedBooks(BaseModel):
    items: list[BookRead]
    page: int
    page_size: int
    total: int
    total_pages: int

class PaginatedLoans(BaseModel):
    items: list[LoanRead]
    page: int
    page_size: int
    total: int
    total_pages: int

class TopBorrower(BaseModel):
    member: MemberRead
    total_loans: int

class OverdueLoanReport(BaseModel):
    loan_id: int
    member_name: str
    book_title: str
    due_date: date
    days_overdue: int

class BookLoanHistoryItem(BaseModel):
    id: int
    member_id: int
    member_name: str
    loan_date: date
    due_date: date
    return_date: date | None = None

class PaginatedBookLoanHistory(BaseModel):
    items: list[BookLoanHistoryItem]
    page: int
    page_size: int
    total: int
    total_pages: int

# Helper for calculating pages
def calculate_total_pages(total: int, page_size: int) -> int:
    if total == 0:
        return 0
    return ceil(total / page_size)