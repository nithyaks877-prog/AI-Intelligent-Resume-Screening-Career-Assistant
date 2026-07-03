import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from backend.database.database import get_db
from backend.database.models import User
from backend.schemas.auth_schemas import SignupRequest, LoginRequest, TokenResponse
from backend.schemas.google_auth_schema import GoogleLoginRequest
from backend.schemas.reset_schemas import ForgotPasswordRequest, ResetPasswordRequest
from backend.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_reset_token,
    decode_reset_token
)
from ml.email_service import send_password_reset_email

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@router.get("/")
def auth_home():
    return {
        "message": "Authentication API Working"
    }


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == payload.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists."
        )

    new_user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        role=payload.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

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


@router.post("/google", response_model=TokenResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Verifies a Google ID token, then either logs in an existing
    user (matched by email) or creates a new account.
    """

    try:
        idinfo = id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token."
        )

    email = idinfo.get("email")
    name = idinfo.get("name", email)

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google account has no email available."
        )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        # New account — no real password since they're using Google.
        # We still store a securely hashed random value to satisfy
        # the non-nullable password column.
        import secrets
        random_password = secrets.token_urlsafe(32)

        user = User(
            name=name,
            email=email,
            password=hash_password(random_password),
            role=payload.role
        )
        db.add(user)
        db.commit()
        db.refresh(user)

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


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Sends a password reset email if the account exists.

    Always returns the same generic message whether or not the
    email is registered — this prevents attackers from using this
    endpoint to discover which emails have accounts.
    """

    user = db.query(User).filter(User.email == payload.email).first()

    generic_message = {
        "message": "If an account exists with that email, a reset link has been sent."
    }

    if not user:
        return generic_message

    reset_token = create_reset_token(user.id)
    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"

    try:
        send_password_reset_email(user.email, reset_link)
    except Exception:
        # Don't leak email-sending errors to the client —
        # log-worthy server-side, but the response stays generic.
        pass

    return generic_message


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Verifies the reset token and updates the user's password.
    """

    token_data = decode_reset_token(payload.token)

    if token_data is None:
        raise HTTPException(
            status_code=400,
            detail="This reset link is invalid or has expired. Please request a new one."
        )

    user = db.query(User).filter(User.id == token_data["user_id"]).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    user.password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password reset successfully. You can now log in."}
