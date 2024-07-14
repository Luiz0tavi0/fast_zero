from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(
        username='luiz', password='a1s23d1as3d1as', email='luiz@gmail.com'
    )

    session.add(user)
    session.commit()

    result: User | None = session.scalar(
        select(User).where(User.email == 'luiz@gmail.com')
    )
    assert result.username == 'luiz' if result is not None else False
