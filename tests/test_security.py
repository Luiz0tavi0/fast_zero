from jwt import decode

from fast_zero.security import create_access_token
from fast_zero.settings import Settings

settings = Settings()  # type: ignore


def test_jwt():
    data = {'sub': 'test@test.com'}
    result = create_access_token(data)
    decoded = decode(result, settings.SECRET_KEY, [settings.ALGORITHM])

    assert decoded['sub'] == data['sub']
    assert decoded['exp']
