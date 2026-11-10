import pytest

from app.modules.users.models import UserRecord
from app.modules.users.service import (
    EmailAlreadyRegisteredError,
    InvalidUserDataError,
    UserService,
)
from tests.modules.users.conftest import EMAIL, PASSWORD

pytestmark = pytest.mark.anyio


async def test_create_user_normalizes_email_and_hashes_password(user: UserRecord) -> None:
    assert user.email == EMAIL
    assert user.password_hash.startswith("$argon2")
    assert PASSWORD not in user.password_hash


async def test_create_user_rejects_duplicate_email(
    user_service: UserService, user: UserRecord
) -> None:
    with pytest.raises(EmailAlreadyRegisteredError):
        await user_service.create_user(" ANA@example.com", "Outra Ana", PASSWORD)


@pytest.mark.parametrize(
    ("email", "name", "password"),
    [("sem-arroba", "Ana", PASSWORD), (EMAIL, "  ", PASSWORD), (EMAIL, "Ana", "curta")],
    ids=["invalid-email", "blank-name", "short-password"],
)
async def test_create_user_rejects_invalid_data(
    user_service: UserService, email: str, name: str, password: str
) -> None:
    with pytest.raises(InvalidUserDataError):
        await user_service.create_user(email, name, password)
