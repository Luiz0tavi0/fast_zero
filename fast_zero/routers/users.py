from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated[SQLAlchemySession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    UserExistsException = HTTPException(status_code=HTTPStatus.BAD_REQUEST)

    if db_user:
        if db_user.username == user.username:
            UserExistsException.detail = 'Username already exists'
            raise UserExistsException
        elif db_user.email == user.email:
            UserExistsException.detail = 'Email already exists'
            raise UserExistsException
    db_user = User(
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    session: T_Session,
    limit: int = 10,
    skip: int = 0,
):
    users = session.scalars(select(User).limit(limit).offset(skip))
    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
def udpate_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission'
        )

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)

    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser
):
    # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permission'
        )
    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


@router.get('/{user_id}', response_model=UserPublic)
def get_user_by_id(user_id: int, session: T_Session):
    db_user = session.scalar(select(User).where(User.id == user_id))
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return db_user
