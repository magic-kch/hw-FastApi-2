import datetime
from typing import Literal
import uuid
from pydantic import BaseModel


class IdResponseBase(BaseModel):
    id: int


class StatusResponse(BaseModel):
    status: Literal["deleted"]


class GetAdsResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    user_id: int
    created_at: datetime.datetime


class CreateAdsRequest(BaseModel):
    title: str
    description: str
    price: int
    # user_id: int


class CreateAdsResponse(IdResponseBase):
    pass


class UpdateAdsRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None


class UpdateAdsResponse(IdResponseBase):
    pass


class DeleteAdsResponse(StatusResponse):
    pass

class BaseUserRequest(BaseModel):
    name: str
    password: str


class CreateUserRequest(BaseUserRequest):
    email: str


class CreateUserResponse(IdResponseBase):
    pass


class LoginRequest(BaseUserRequest):
    pass

class LoginResponse(BaseModel):
    token: uuid.UUID
