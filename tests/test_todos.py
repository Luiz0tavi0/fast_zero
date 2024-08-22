import random
import urllib.parse
from http import HTTPStatus
from itertools import product
from typing import Dict, List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fast_zero.models import TodoState, User
from tests.conftest import TodoFactory


def test_create_todo(client: TestClient, token: str):
    response = client.post(
        url='/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test Todo',
            'description': 'Test Todo Description',
            'state': 'draft',
        },
    )

    assert response.json() == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'Test Todo Description',
        'state': 'draft',
    }


def test_list_todos_should_return_5_todos(
    session: Session, client: TestClient, user: User, token: str
):
    EXPECTED_TODOS = 5
    todos = TodoFactory.create_batch(5, user_id=user.id)
    session.bulk_save_objects(todos)
    session.commit()

    response = client.get(
        url='/todos/', headers={'Authorization': f'Bearer {token}'}
    )
    # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415

    assert response.status_code == HTTPStatus.OK
    responsed_todos = len(response.json()['todos'])

    assert responsed_todos == EXPECTED_TODOS


def get_attribute(field):
    return lambda instance: getattr(instance, field)


def generate_params(fields: List[str], list_qtys: List[int]):
    """
    Gera parâmetros para os testes, incluindo diferentes campos e quantidades.

    Args:
        fields (List[str]): Lista de campos a serem testados.
        list_qtys (List[int]): Lista de quantidades para cada campo.

    Yields:
        pytest.param: Parâmetros parametrizados para pytest.
    """

    for field, qty in product(fields, list_qtys):
        get_field_value = get_attribute(field)

        yield pytest.param(
            field,
            qty,
            list(map(get_field_value, TodoFactory.build_batch(qty))),
            id=f'field={field}_qty={qty}',
        )


@pytest.mark.parametrize(
    ('field', 'qty', 'values_for_field'),
    generate_params(['title', 'description'], [1, 10, 25, 50, 100]),
)
def test_list_todos_should_return_all_todos_contains_value(  # noqa: PLR0913, PLR0917
    session: Session,
    client: TestClient,
    user: User,
    token: str,
    qty: int,
    values_for_field: List[str],
    field: str,
):
    # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415
    # Cria uma lista de todos com o campo especificado incluindo tokens
    todos = TodoFactory.create_batch(qty, user_id=user.id)
    for todo, value in zip(todos, values_for_field):
        # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415
        field_value = getattr(todo, field)
        position_insert = random.randint(0, (len(field_value) - 1))
        field_chars: List[str] = list(field_value)
        field_chars[position_insert] = value

        setattr(todo, field, ''.join(field_chars))

    session.bulk_save_objects(todos)
    session.commit()

    # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415

    # Executa o teste para verificar se todos os tokens estão
    # presentes nos campos especificados dos todos
    for value in values_for_field:
        encoded_value = urllib.parse.quote(value)
        # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415
        response = client.get(
            url=f'/todos/?{field}={encoded_value}',
            headers={'Authorization': f'Bearer {token}'},
        )
        # import ipdb; ipdb.set_trace()  # noqa: E702, I001, I001, PLC0415
        assert response.status_code == HTTPStatus.OK
        response_todos = response.json().get('todos', [])
        # Espera que cada token retorne exatamente 1 todo
        assert len(response_todos) == 1
        assert all(value in todo[field] for todo in response_todos)


@pytest.mark.parametrize('qty', [2, 5, 10])
@pytest.mark.parametrize(
    'state',
    [
        TodoState.draft,
        TodoState.todo,
        TodoState.state,
        TodoState.doing,
        TodoState.done,
        TodoState.trash,
    ],
)
def test_list_todos_should_return_all_todos_by_state(  # noqa: PLR0913 PLR0917
    session: Session,
    client: TestClient,
    user: User,
    token: str,
    state: TodoState,
    qty: int,
):
    todos = TodoFactory.build_batch(qty, state=state, user_id=user.id)
    session.bulk_save_objects(todos)
    session.commit()

    response = client.get(
        url=f'/todos/?state={state.value}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    db_todos = response.json()['todos']
    assert all([db_todo['state'] == state.value for db_todo in db_todos])


@pytest.mark.parametrize(
    ('offset', 'limit', 'expected_length'),
    [
        (0, 5, 5),
        (5, 5, 5),
        (10, 5, 5),
        (15, 5, 5),
        (18, 2, 2),
        (19, 1, 1),
        (20, 5, 0),
        (4, 2, 2),
        (8, 4, 4),
        (18, 5, 2),
        (0, 10, 10),
        (10, 10, 10),
        (0, 20, 20),
        (0, 25, 20),
        (5, 15, 15),
        (7, 3, 3),
        (13, 7, 7),
        (9, 11, 11),
        (19, 2, 1),
        (15, 10, 5),
        (2, 6, 6),
        (3, 5, 5),
        (6, 4, 4),
        (12, 8, 8),
        (16, 3, 3),
        (1, 9, 9),
        (11, 5, 5),
        (14, 6, 6),
        (17, 4, 3),
        (20, 1, 0),
        (0, 1, 1),
        (1, 1, 1),
        (2, 1, 1),
        (3, 1, 1),
        (4, 1, 1),
        (0, 15, 15),
        (15, 1, 1),
        (15, 6, 5),
        (5, 10, 10),
        (9, 10, 10),
        (4, 0, 0),
        (11, 1, 1),
        (6, 7, 7),
        (8, 12, 12),
        (14, 2, 2),
    ],
)
def test_list_todos_pagination_should_return_expected_number_of_todos(  # noqa: PLR0913, PLR0917
    session: Session,
    client: TestClient,
    user: User,
    token: str,
    offset: int,
    limit: int,
    expected_length: int,
):
    """
    Testa a paginação da listagem de TODO'S, verificando se retorna a
    quantidade correta de TODO'S conforme os parâmetros offset e limit.
    """
    # Cria 20 todos para o usuário especificado
    todos = TodoFactory.build_batch(20, user_id=user.id)
    session.bulk_save_objects(todos)
    # Certifique-se de que os todos são salvos no banco de dados
    session.commit()

    response = client.get(
        url='/todos/',
        params={'offset': offset, 'limit': limit},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    db_todos = response.json()['todos']
    assert len(db_todos) == expected_length


def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


def test_delete_todo_error(client, token):
    response = client.delete(
        f'/todos/{10}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def generate_values_to_path(qty: int, fields: List[str]):
    """
    Gera parâmetros para os testes.

    Args:
        qty (int): Lista de campos a serem testados.
        fields (List[str]): Lista de quantidades para cada campo.

    Yields:
        pytest.param: Parâmetros parametrizados para pytest.
    """

    for n in range(qty):
        for field in fields:
            get_field_value = get_attribute(field)
            yield pytest.param(
                {field: get_field_value(TodoFactory.build())},
                id=f'field={field}_n={n + 1}_t={qty}',
            )


@pytest.mark.parametrize(
    'value_for_patch',
    generate_values_to_path(qty=50, fields=['title', 'description', 'state']),
)
def test_patch_todo(  # noqa: PLR0913, PLR0917
    session,
    client,
    user: User,
    token: str,
    value_for_patch: Dict[str, str | TodoState],
):
    # ipdb.set_trace()  # noqa: E702, F401, F821, I001, PLC0415
    # session, client, user, token, title, description, state: TodoState
    # Arrange
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    # ipdb.set_trace()  # noqa: E702, F401, F821, I001, PLC0415

    update_data = value_for_patch.copy()

    # ipdb.set_trace()  # noqa: E702, F401, F821, I001, PLC0415
    # Act
    response = client.patch(
        url=f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json=update_data,
    )

    # Assert
    assert response.status_code == HTTPStatus.OK

    # Fetch the updated todo from the database
    updated_todo = response.json()

    for field, updated_value in update_data.items():
        # ipdb.set_trace()  # noqa: E702, F401, F821, I001, PLC0415
        assert updated_todo[field] == updated_value


def test_patch_todo_must_be_fail_with_inexistent_todo(
    client: TestClient, user: User, token: str, session
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.patch(
        url=f'/todos/{15}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': todo.title},
    )
    assert response.json()['detail'] == 'Task not found.'
    assert response.status_code == HTTPStatus.NOT_FOUND
