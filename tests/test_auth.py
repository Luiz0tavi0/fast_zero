import datetime
import secrets
from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time
from sqlalchemy import delete
from sqlalchemy.orm import Session

from fast_zero.models import User
from fast_zero.security import create_access_token


def test_get_token(client: TestClient, user):
    response = client.post(
        url='/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_token_expired_after_time(client, user):
    with freeze_time('2023-07-14 12:00:00', tz_offset=0):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00', tz_offset=0):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client, token: str):
    response = client.get(
        url='/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.json()['access_token']
    assert response.json()['token_type'] == 'Bearer'
    assert response.status_code == HTTPStatus.OK


def test_token_expired_dont_refresh(client, user, token: str):
    initial_datetime = datetime.datetime.now(tz=datetime.UTC)

    future_datetime = initial_datetime + datetime.timedelta(minutes=30)

    auth_header = {'Authorization': f'Bearer {token}'}
    with freeze_time(future_datetime, tz_offset=0, tick=True):
        response = client.get(url='/auth/refresh_token', headers=auth_header)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_wrong_password(client, user):
    password = f'{secrets.token_urlsafe(7)}wrong{user.clean_password}'

    response = client.post(
        url='/auth/token',
        data={
            'username': user.email,
            'password': password,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_wrong_email(client, user):
    wrong_email = f"{user.email.split('@')[0][::-1]}{secrets.token_urlsafe(7)}"
    wrong_email += f"@{user.email.split('@')[1]}"
    response = client.post(
        url='/auth/token',
        data={'username': wrong_email, 'password': user.clean_password},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_current_user_with_invalid_credentials(
    client: TestClient, token: str
):
    auth_header = {'Authorization': f'Bearer {token[::-1]}'}

    response = client.get(url='/auth/refresh_token', headers=auth_header)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_without_username(client: TestClient):
    token_without_username = create_access_token({})
    auth_header = {'Authorization': f'Bearer {token_without_username}'}

    response = client.get(url='/auth/refresh_token', headers=auth_header)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_with_inexistent_user(
    client: TestClient, token: str, session: Session
):
    session.execute(delete(User))
    session.commit()
    auth_header = {'Authorization': f'Bearer {token}'}

    response = client.get(url='/auth/refresh_token', headers=auth_header)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
