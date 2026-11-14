from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from todo_chat.database import get_session
from todo_chat.models import User
from todo_chat.schema import AuthResponse, CurrentUserResponse, LoginRequest, UserCreate
from todo_chat.security import create_access_token, dummy_hash, get_current_user, password_hash

router = APIRouter(prefix="/auth", tags=["authentication"])
DatabaseSession = Annotated[Session, Depends(get_session)]


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(payload: UserCreate, request: Request, session: DatabaseSession):
    email = str(payload.email).casefold()
    if session.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(400, "Email is already registered")
    user = User(
        name=payload.name, email=email,
        password_hash=password_hash.hash(payload.password),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        # A concurrent signup may have won the unique-email constraint.
        if session.scalar(select(User.id).where(User.email == email)) is not None:
            raise HTTPException(400, "Email is already registered") from None
        raise
    session.refresh(user)
    return {"token": create_access_token(user.id, request.app.state.settings), "user": user}


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, request: Request, session: DatabaseSession):
    user = session.scalar(select(User).where(User.email == str(payload.email).casefold()))
    valid = password_hash.verify(payload.password, user.password_hash if user else dummy_hash)
    if user is None or not valid:
        raise HTTPException(
            401, "Invalid email or password", headers={"WWW-Authenticate": "Bearer"}
        )
    return {"token": create_access_token(user.id, request.app.state.settings), "user": user}


@router.get("/me", response_model=CurrentUserResponse)
def current_user(user: Annotated[User, Depends(get_current_user)]):
    return {"user": user}
