
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash

# from fast_zero.models import User


@pytest.fixture()
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as test_client:
        app.dependency_overrides[get_session] = get_session_override

        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)
    with Session(engine) as sess:
        yield sess
    table_registry.metadata.drop_all(engine)


@pytest.fixture()
def user(session):
    pwd = 'testtest'
    user = User(
        username='test', email='test@test.com', password=get_password_hash(pwd)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    user.__setattr__('clean_password', pwd)  # noqa: PLC2801
    return user


@pytest.fixture()
def token(client: TestClient, user: User):
    response = client.post(
        url='/auth/token',
        data={'username': user.email, 'password': user.clean_password},  # type: ignore
    )

    return response.json()['access_token']
