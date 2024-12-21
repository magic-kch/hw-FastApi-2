import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from auth import hash_password
from config import ADMIN_NAME, ADMIN_PASSWORD, ADMIN_EMAIL
from models import Session, User


async def create_administrator(session: AsyncSession, name: str, email: str, password: str):
    user = User(name=name, email=email, password=hash_password(password), role="admin")
    session.add(user)
    await session.commit()


async def main():
    async with Session() as session:
        await create_administrator(session, ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD)


if __name__ == "__main__":
    asyncio.run(main())
