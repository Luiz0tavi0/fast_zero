from http import HTTPStatus

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from fast_zero.routers.users import create_user
from fast_zero.schemas import UserPublic, UserSchema


def test_create_user(client: TestClient):
    response = client.post(
        '/users/',
        json={
            'email': 'test@gmail.com',
            'username': 'tester',
            'password': 'teste123456789',
        },
    )
    assert response.json() == {
        'id': 1,
        'email': 'test@gmail.com',
        'username': 'tester',
    }


def test_read_users(client: TestClient):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_user(client: TestClient, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client: TestClient, user, token: str):
    response = client.put(
        url=f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'password': 'aBx_123458791',
            'id': 1,
            'email': 'luiz2@gmail.com',
            'username': 'teste_user_name_2',
        },
    )
    assert response.json() == {
        'id': 1,
        'email': 'luiz2@gmail.com',
        'username': 'teste_user_name_2',
    }


def test_delete_user(client: TestClient, user, token: str):
    response = client.delete(
        url=f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'message': 'User deleted'}


def test_delete_wrong_user(client: TestClient, user, token: str):
    response = client.delete(
        url=f'/users/{user.id + 1}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}


def test_create_user_deve_levantar_HTTPException_para_email_existente(
    session, user
):
    user_schema = UserSchema.model_validate(user).model_dump()

    user_schema['username'] = f'1_{user_schema['username'][::-1]}_$'
    with pytest.raises(HTTPException) as exc_info:
        create_user(UserSchema(**user_schema), session)

    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.detail == 'Email already exists'


def test_create_user_deve_levantar_HTTPException_para_username_existente(
    session, user
):
    user_schema = UserSchema.model_validate(user).model_dump()

    user_schema['email'] = (
        f'1_{user_schema['email'].split('@')[0][::-1]}@{user_schema['email'].split('@')[1]}'
    )
    with pytest.raises(HTTPException) as exc_info:
        create_user(UserSchema(**user_schema), session)

    assert exc_info.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc_info.value.detail == 'Username already exists'


def test_create_user_deve_retornar_400_e_username_already_exists(client, user):
    user_schema = UserSchema.model_validate(user).model_dump()
    user_schema['email'] = (
        f'1_{user_schema['email'].split('@')[0][::-1]}@{user_schema['email'].split('@')[1]}'
    )

    response = client.post('/users/', json=user_schema)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Username already exists'


def test_create_user_deve_retornar_400_e_email_already_exists(client, user):
    user_schema = UserSchema.model_validate(user).model_dump()
    user_schema['username'] = f'1_{user_schema["username"][::-1]}_$'

    response = client.post('/users/', json=user_schema)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Email already exists'


def test_get_user_by_id_deve_retornar_user_public(client: TestClient, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == user_schema
