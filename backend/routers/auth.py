from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User
from backend.schemas.auth_schemas import SignupRequest, LoginRequest, TokenResponse
from backend.utils.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.get("/")
def auth_home():
    return {
        "message": "Authentication API Working"
    }


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):

    # Check if the email is already registered
    existing_user = db.query(User).filter(User.email == payload.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists."
        )

    # Create new user with a hashed password
    new_user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        role=payload.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate a token immediately so the user is logged in after signup
    token = create_access_token({
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    })

    return TokenResponse(
        access_token=token,
        role=new_user.role,
        name=new_user.name
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    })

    return TokenResponse(
        access_token=token,
        role=user.role,
        name=user.name
    )
