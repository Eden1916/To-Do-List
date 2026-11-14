from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from todo_chat.config import Settings
from todo_chat.database import get_session
from todo_chat.models import User

password_hash = PasswordHash.recommended()
# Unknown users still perform a password verification, like existing users.
dummy_hash = password_hash.hash("not-a-real-user-password")
bearer = HTTPBearer(auto_error=False)
ISSUER = "todo-chat"
AUDIENCE = "todo-chat-api"


def create_access_token(user_id: int, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(user_id), "iat": now,
         "exp": now + timedelta(minutes=settings.access_token_minutes),
         "iss": ISSUER, "aud": AUDIENCE},
        settings.jwt_secret.get_secret_value(), algorithm="HS256",
    )


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    unauthorized = HTTPException(
        status_code=401, detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(
            credentials.credentials,
            request.app.state.settings.jwt_secret.get_secret_value(),
            algorithms=["HS256"], issuer=ISSUER, audience=AUDIENCE,
            options={"require": ["sub", "iat", "exp"]},
        )
        user_id = int(payload["sub"])
        if user_id < 1 or user_id > 2**63 - 1:
            raise ValueError("Invalid user ID")
    except (jwt.InvalidTokenError, ValueError):
        raise unauthorized from None
    user = session.get(User, user_id)
    if user is None:
        raise unauthorized
    return user
