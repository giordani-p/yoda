import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import UserRecord
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService

EMAIL = "ana@example.com"
PASSWORD = "correct-horse-battery"


@pytest.fixture
def user_service(db_session: AsyncSession) -> UserService:
    return UserService(UserRepository(db_session))


@pytest.fixture
async def user(user_service: UserService) -> UserRecord:
    return await user_service.create_user(EMAIL, "Ana", PASSWORD)
