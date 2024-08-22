from http import HTTPStatus

from fastapi.testclient import TestClient


def test_read_root_dever_retornar_ok_e_olar_mundo(client: TestClient):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}
