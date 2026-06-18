from fastapi import APIRouter, HTTPException
from app.schemas.resume_schema import UserRegister, UserLogin, TokenResponse
from app.auth.security import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
_users: dict = {}
_next_id: int = 1

@router.post("/register", status_code=201)
def register(user: UserRegister):
    global _next_id
    if user.email in users:
        raise HTTPException(
            status_code=409,
            detail=f"Email {user.email} already registered"
        )

    _users[user.email] = {
        "id": _next_id,
        "email": user.email,
        "password": hash_password(user.password),
    }
    _next_id+=1
    return{
        "message": "Registered successfully",
        "email": user.email
    }

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    stored = _users.get(credentials.email)

    if not stored or not verify_password(
        credentials.password, stored["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    token = create_token(
        user_id=stored["id"],
        email=stored["email"]
    )

    return{
        "access_token": token,
        "token_type": "bearer"
    }