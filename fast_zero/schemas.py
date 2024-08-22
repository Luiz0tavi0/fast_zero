from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from fast_zero.models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    model_config = ConfigDict(from_attributes=True)


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: List[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState
    model_config = ConfigDict(from_attributes=True)


class TodoPublic(TodoSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TodoList(BaseModel):
    todos: List[TodoPublic]


class TodoUpdate(TodoSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[TodoState] = None
