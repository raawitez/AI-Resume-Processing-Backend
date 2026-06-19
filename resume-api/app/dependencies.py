from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.auth.security import decode_token

bearer_scheme = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db:    Session = Depends(get_db)
) -> dict:
    error = HTTPException(
        status_code=401,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise error

    user_id = payload.get("sub")
    email   = payload.get("email")

    if not user_id:
        raise error

    return {
        "user_id": int(user_id),
        "email":   email
    }