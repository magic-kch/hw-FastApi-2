import datetime
import uuid

from custom_types import Role
from config import PG_DSN
from sqlalchemy import DateTime, Integer, String, func, UUID, ForeignKey, CheckConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

engine = create_async_engine(
    PG_DSN,
)

Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):

    @property
    def id_dict(self):
        return {"id": self.id}


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        CheckConstraint("role in ('user', 'admin')"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(72), nullable=False)
    tokens: Mapped[list["Token"]] = relationship("Token",
                                                 back_populates="user",
                                                 cascade="all, delete-orphan",
                                                 lazy="joined")
    ads: Mapped[list["Advertisement"]] = relationship("Advertisement",
                                                      back_populates="user",
                                                      cascade="all, delete-orphan",
                                                      lazy="joined")
    role: Mapped[Role] = mapped_column(String(20), default="user")

    @property
    def dict(self):
        return {"id": self.id,
                "name": self.name,
                "email": self.email
                }

class Token(Base):
    __tablename__ = "token"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(User, back_populates="tokens", lazy="joined")

    @property
    def dict(self):
        return {"token": self.token}


class Advertisement(Base):
    __tablename__ = "advertisement"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    # author: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(User, back_populates="ads", lazy="joined")

    @property
    def dict(self):
        return {"id": self.id,
                "title": self.title,
                "description": self.description,
                "price": self.price,
                # "author": self.author,
                "created_at": self.created_at
                }


ORM_OBJ = Advertisement | User | Token
ORM_CLS = type[Advertisement] | type[User] | type[Token]


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()