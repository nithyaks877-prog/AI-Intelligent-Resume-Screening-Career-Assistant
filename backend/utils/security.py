import os
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from jose import jwt, JWTError

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

if not SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY not found. Make sure it's set in your .env file."
    )

# -----------------------------
# Password Hashing (using bcrypt directly)
# -----------------------------
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


# -----------------------------
# JWT Token Creation
# -----------------------------
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# -----------------------------
# JWT Token Verification
# -----------------------------
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# -----------------------------
# Password Reset Token
# (separate, short-lived, purpose-tagged token —
#  cannot be used to access protected routes)
# -----------------------------
RESET_TOKEN_EXPIRE_MINUTES = 30


def create_reset_token(user_id: int) -> str:
    to_encode = {
        "user_id": user_id,
        "purpose": "password_reset"
    }

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=RESET_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_reset_token(token: str):
    """
    Returns the payload only if the token is valid AND
    was specifically created for password resets.
    """
    payload = decode_access_token(token)

    if payload is None:
        return None

    if payload.get("purpose") != "password_reset":
        return None

    return payload


