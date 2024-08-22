from http import HTTPStatus
from typing import Annotated, Optional

# import ipdb  # noqa: F401
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from fast_zero.database import get_session
from fast_zero.models import Todo, TodoState, User
from fast_zero.schemas import (
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fast_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated[SQLAlchemySession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
def create_todo(todo: TodoSchema, session: T_Session, user: CurrentUser):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def list_todos(  # noqa
    session: T_Session,
    user: CurrentUser,
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    state: Optional[TodoState] = Query(None),
    offset: int = Query(0),
    limit: int = Query(10),
):
    # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415
    query = select(Todo).where(Todo.user_id == user.id)
    # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415
    if title:
        query = query.filter(Todo.title.ilike(f'%{title}%', escape='\\'))

    if description:
        query = query.filter(
            Todo.description.ilike(f'%{description}%', escape='\\')
        )

    if state:
        query = query.filter(Todo.state == state)

    todos = session.execute(query.offset(offset).limit(limit)).scalars().all()

    # Retornando os dados como um dicionário com a chave `todos`
    return TodoList(todos=[TodoPublic.model_validate(todo) for todo in todos])


@router.patch('/{todo_id}', response_model=TodoPublic)
def patch_todo(
    todo_id: int, session: T_Session, user: CurrentUser, todo: TodoUpdate
):
    db_todo = session.scalar(
        select(Todo).where((Todo.user_id == user.id) & (Todo.id == todo_id))
    )
    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(todo_id: int, session: T_Session, user: CurrentUser):
    todo = session.scalar(
        select(Todo).where((Todo.user_id == user.id) & (Todo.id == todo_id))
    )
    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )
    session.delete(todo)
    session.commit()

    return Message(message='Task has been deleted successfully.')
