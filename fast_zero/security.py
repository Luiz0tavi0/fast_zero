from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, PyJWTError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.settings import Settings

settings = Settings()  # type: ignore
pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})

    encoded_jwt = encode(
        to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_current_user(
    session: Session = Depends(get_session), token=Depends(oauth2_scheme)
):
    # breakpoint()
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415
    try:
        payload = decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={'verify_exp': True},
        )
        username: str = payload.get('sub')
        if not username:
            raise credentials_exception

    except ExpiredSignatureError:
        raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user_db = session.scalar(select(User).where(User.email == username))

    if not user_db:
        raise credentials_exception

    return user_db
