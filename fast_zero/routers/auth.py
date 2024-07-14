from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=['auth'])
T_Session = Annotated[SQLAlchemySession, Depends(get_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
def login_for_access_token(session: T_Session, form_data: T_OAuth2Form):
    user = session.scalar(select(User).where(User.email == form_data.username))
    # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}
