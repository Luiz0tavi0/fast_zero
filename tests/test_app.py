from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_dever_retornar_ok_e_olar_mundo():
    client = TestClient(app=app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Ola mundo.'}
