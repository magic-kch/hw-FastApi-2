import datetime

from auth import check_password, hash_password
import crud
import pydantic
from constants import STATUS_DELETED
from dependency import SessionDependency, TokenDependency
from fastapi import FastAPI, Query, HTTPException
from lifespan import lifespan
from models import Advertisement, User, Token
from schema import (
    CreateAdsRequest,
    CreateAdsResponse,
    DeleteAdsResponse,
    GetAdsResponse,
    UpdateAdsRequest,
    UpdateAdsResponse,
    LoginRequest,
    LoginResponse,
    CreateUserRequest,
    CreateUserResponse
)

app = FastAPI(
    title="Advertisements API",
    terms_of_service="",
    description="Sell or Buy advertisements",
    lifespan=lifespan,
)


@app.post("/advertisement", response_model=CreateAdsResponse, tags=["advertisements"])
async def create_item(item: CreateAdsRequest,
                      session: SessionDependency,
                      token: TokenDependency):
    ad = Advertisement(
        title=item.title,
        description=item.description,
        price=item.price,
        user_id=token.user_id,
    )
    await crud.add_item(session, ad)
    return ad.id_dict


@app.patch("/advertisement/{advertisement_id}", response_model=UpdateAdsResponse, tags=["advertisements"])
async def update_item(advertisement_id: int,
                      item: UpdateAdsRequest,
                      session: SessionDependency,
                      token: TokenDependency):
    json_data = item.dict(exclude_unset=True, by_alias=True)
    ad = await crud.get_item_by_id(session, Advertisement, advertisement_id)

    if ad.user_id != token.user_id and token.user.role != "admin":
        raise HTTPException(403, "Forbidden")

    for key, value in json_data.items():
        setattr(ad, key, value)

    await crud.add_item(session, ad)
    return ad.id_dict


@app.delete("/advertisement/{advertisement_id}", response_model=DeleteAdsResponse, tags=["advertisements"])
async def delete_item(advertisement_id: int,
                      session: SessionDependency,
                      token: TokenDependency):
    ad = await crud.get_item_by_id(session, Advertisement, advertisement_id)
    if ad.user_id != token.user_id and token.user.role != "admin":
        raise HTTPException(403, "Forbidden")
    await crud.add_item(session, ad)
    return STATUS_DELETED


@app.get("/advertisement/{advertisement_id}", response_model=GetAdsResponse, tags=["advertisements"])
async def get_item(advertisement_id: int, session: SessionDependency):
    ad = await crud.get_item_by_id(session, Advertisement, advertisement_id)
    return ad.dict


@app.get("/advertisement", response_model=list[GetAdsResponse], tags=["advertisements"])
async def get_advertisement(session: SessionDependency,
                            title: str = Query(None),
                            description: str = Query(None),
                            price: int = Query(None),
                            user_id: int = Query(None)):
    search_params = {}
    if title:
        search_params["title"] = title
    if description:
        search_params["description"] = description
    if price:
        search_params["price"] = price
    if user_id:
        search_params["author"] = user_id

    ad = await crud.get_items_by_params(session, Advertisement, **search_params)
    return ad.scalars().all()



@app.post("/user", response_model=CreateUserResponse, tags=["user"])
async def create_user(user_create: CreateUserRequest, session: SessionDependency):
    user = User(
        name=user_create.name,
        email=user_create.email,
        password=hash_password(user_create.password),
    )
    await crud.add_item(session, user)
    return user.id_dict

@app.patch("/user/{user_id}", response_model=CreateUserResponse, tags=["user"])
async def update_user(user_id: int,
                      user_update: CreateUserRequest,
                      session: SessionDependency,
                      token: TokenDependency):
    json_data = user_update.dict(exclude_unset=True, by_alias=True)
    user = await crud.get_item_by_id(session, User, user_id)

    if user.id != token.user_id and token.user.role != "admin":
        raise HTTPException(403, "Forbidden")

    if json_data.get("password"):
        json_data["password"] = hash_password(json_data["password"])

    for key, value in json_data.items():
        setattr(user, key, value)

    await crud.add_item(session, user)
    return user.id_dict

@app.delete("/user/{user_id}", response_model=CreateUserResponse, tags=["user"])
async def delete_user(user_id: int,
                      session: SessionDependency,
                      token: TokenDependency):
    user = await crud.get_item_by_id(session, User, user_id)

    if user.id != token.user_id and token.user.role != "admin":
        raise HTTPException(403, "Forbidden")

    await crud.add_item(session, user)
    return STATUS_DELETED


@app.get("/user/{user_id}", response_model=CreateUserResponse, tags=["user"])
async def get_user(user_id: int, session: SessionDependency):
    user = await crud.get_item_by_id(session, User, user_id)
    return user.dict


@app.post("/login", response_model=LoginResponse, tags=["user"])
async def login(login_request: LoginRequest, session: SessionDependency):
    user = await crud.get_items_by_params(session, User, name=login_request.name)
    user = user.scalars().first()
    if user and check_password(login_request.password, user.password):
        token = Token(user_id=user.id)
        await crud.add_item(session, token)
        return token.dict
