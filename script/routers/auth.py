import hashlib
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.responses import JSONResponse, HTMLResponse, Response

from script import json_db


class Message(BaseModel):
    message: str


class auth_token(BaseModel):
    exp: int
    token: str
    sub_token: str


router = APIRouter()

user_db = json_db.DB("users.json")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # 15分で有効期限が切れるトークンを生成

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "SECRET_KEY", algorithm="ALGORITHM")
    return encoded_jwt


@router.post("/users/register/",
             summary='sign in',
             description='create your account',
             response_description='None',
             tags=["Auth"],
             responses={200: {"model": Message},
                        409: {"model": Message}})
async def create_account(auth_data: OAuth2PasswordRequestForm = Depends()):
    user_db.load()
    user_id = hashlib.sha256(auth_data.username.encode("utf-8")).hexdigest()
    if user_id in user_db():
        return Response(status_code=status.HTTP_409_CONFLICT)
    else:
        hash_ps = hashlib.sha256(auth_data.password.encode("utf-8")).hexdigest()
        user_db()[user_id] = {
            "username": auth_data.username,
            "password": hash_ps
        }
        user_db.dump()
        return Response(status_code=status.HTTP_201_CREATED)


@router.post("/users/login/",
             summary='log in',
             description='create access token',
             response_description='None',
             tags=["Auth"],
             responses={201: {"model": Message},
                        401: {"model": Message}})
async def get_access_token(auth_data: OAuth2PasswordRequestForm = Depends()):

    user_db.load()
    user_id = hashlib.sha256(auth_data.username.encode("utf-8")).hexdigest()
    if user_id in user_db():
        return Response(status_code=status.HTTP_201_CREATED)

    return Response(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/users/login/",
            summary='login',
            description='get access token',
            response_description='None',
            tags=["Auth"])
async def get_access_token():
    pass
