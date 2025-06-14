"""Authentication and user management endpoints."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models
from .db import get_db
from .utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Retrieve the current authenticated user."""
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user = db.query(models.User).filter(models.User.id == payload.get("sub")).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/register", summary="Register new user")
async def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Create a user.

    **Example request**::

        username=user&password=secret
    """
    existing = db.query(models.User).filter(models.User.username == form_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(form_data.password)
    user = models.User(username=form_data.username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"username": user.username}


@router.post("/login", summary="Login and obtain JWT")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate and return access and refresh tokens.

    **Example request**::

        username=user&password=secret

    **Example response**::

        {
          "access_token": "...",
          "refresh_token": "...",
          "token_type": "bearer"
        }
    """
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", summary="Refresh JWT")
async def refresh(token: str = Depends(oauth2_scheme)):
    """Issue a new access token using a valid refresh token.

    **Example response**::

        {
          "access_token": "...",
          "token_type": "bearer"
        }
    """
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    new_token = create_access_token({"sub": payload.get("sub")})
    return {"access_token": new_token, "token_type": "bearer"}
