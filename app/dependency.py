import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException
from models import Session, Token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
import crud
from config import TOKEN_TTL_SEC
import datetime

async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session, use_cache=True)]


async  def get_token(
        x_token: Annotated[uuid.UUID, Header()],
        session: SessionDependency
):
    token = await crud.get_items_by_params(
        session,
        Token,
        token=x_token)
    datetime_now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    if token is None or token[0].created_at < datetime_now - datetime.timedelta(seconds=TOKEN_TTL_SEC):
        raise HTTPException(401, "Invalid token")
    # created_at__gt=datetime.datetime.now() - datetime.timedelta(seconds=TOKEN_TTL_SEC))
    return token[0]


TokenDependency = Annotated[Token, Depends(get_token)]
