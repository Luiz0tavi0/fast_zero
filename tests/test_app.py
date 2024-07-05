from http import HTTPStatus


def test_dever_retornar_ok_e_olar_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá mundo!'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'email': 'luiz@gmail.com',
            'username': 'loon',
            'password': '1234567ABC',
        },
    )
    assert response.json() == {
        'id': 1,
        'email': 'luiz@gmail.com',
        'username': 'loon',
    }


def test_read_users(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [{'id': 1, 'email': 'luiz@gmail.com', 'username': 'loon'}]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'password': '123',
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


def test_delet_user(client):
    response = client.delete('/users/1')

    assert response.json() == {'message': 'User deleted'}


def test_update_user_nao_existe_deve_retornar_404_e_user_not_found(client):
    response = client.put(
        '/users/999',
        json={'password': '123', 'id': 999, 'email': 'unknown@gmail.com',
            'username': 'batata_123',
        }
    )
    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == {'detail': 'User not found'}


def test_delete_user_nao_existe_deve_retornar_404_e_user_not_found(client):
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
