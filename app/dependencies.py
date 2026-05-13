import os
from collections.abc import Generator

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal

# This function manages our connection to the database.
# It opens a new session for every request and ensures its closed safely.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db  # Provide the database session to the caller
    finally:
        db.close() # Always close the connection to avoid memory leaks

# This is a security check (middleware) to protect our API.
# It checks if the user has provided the correct 'X-API-Key' in the header.
def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    # Try to find the secret key from the system environment variables
    expected_api_key = os.getenv("LIBRARY_API_KEY")

    # If no key is set in the environment, use a default one for local development
    if not expected_api_key:
        expected_api_key = "dev-secret-key"

    # Compare the key provided by the user with our secret key
    if x_api_key != expected_api_key:
        # If they don't match, block the request with a 401 Unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )