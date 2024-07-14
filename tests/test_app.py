from http import HTTPStatus

from fastapi.testclient import TestClient


def test_read_root_dever_retornar_ok_e_olar_mundo(client: TestClient):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}


def test_get_token(client: TestClient, user):
    response = client.post(
        url='/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token
