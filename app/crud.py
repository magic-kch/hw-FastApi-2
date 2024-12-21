from fastapi import HTTPException
from models import ORM_CLS, ORM_OBJ
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def add_item(session: AsyncSession, item: ORM_OBJ):
    session.add(item)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="record already exist")


async def get_item_by_id(
    session: AsyncSession, orm_cls: ORM_CLS, item_id: int
) -> ORM_OBJ:
    orm_obj = await session.get(orm_cls, item_id)
    if orm_obj is None:
        raise HTTPException(404, "record not found")
    return orm_obj


# async def get_items_by_params(session: AsyncSession, orm_cls: ORM_CLS, **kwargs):
#     query = select(orm_cls).filter_by(**kwargs)#.order_by(orm_cls.created_at.desc())
#     return await session.execute(query)
async def get_items_by_params(session, orm_cls, **kwargs):
    if hasattr(orm_cls, 'created_at'):
        query = select(orm_cls).filter_by(**kwargs).order_by(orm_cls.created_at.desc())
    else:
        query = select(orm_cls).filter_by(**kwargs)
    return await session.execute(query)
#
#     result = await session.execute(query)
#     return result.unique().scalars().all()

async def delete_item(session: AsyncSession, item: ORM_OBJ):
    await session.delete(item)
    await session.commit()
