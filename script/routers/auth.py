import hashlib
from datetime import datetime, timedelta

import jose
from jose import jwt
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi.responses import JSONResponse, Response

from script.DB import json_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# jose jwt
ALGORITHM = "HS256"
KEY = "KEY"


class Message(BaseModel):
    message: str


class auth_token(BaseModel):
    token_type: str
    access_token: str


class auth_info(BaseModel):
    user_id: str = ""
    auth: bool = False
    permission: int = "-1"
    new_token: str = ""

    def __init__(self, user_id, auth, permission, new_token):
        super().__init__()

        self.user_id = user_id
        self.auth = auth
        self.permission = permission
        self.new_token = new_token


router = APIRouter()

user_db = json_db.DB("DB/users.json")


def str_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def create_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(user_id):
    user_db.load()
    user_id_hash = str_hash(user_id)
    token = create_token({"userid": user_db()[user_id_hash]["userid"]}, timedelta(minutes=15))
    user_db()[user_id_hash]["access_token"] = token
    user_db.dump()
    return token


@router.post("/users/register/",
             summary='sign in',
             description='create your account',
             response_description='None',
             tags=["Auth"],
             responses={200: {"model": Message},
                        201: {"model": Message},
                        409: {"model": Message}})
async def create_account(auth_data: OAuth2PasswordRequestForm = Depends()):
    user_db.load()
    user_id = str_hash(auth_data.username)
    if user_id in user_db():
        return Response(status_code=status.HTTP_409_CONFLICT)
    else:
        hash_ps = str_hash(auth_data.password)
        user_db()[user_id] = {
            "permission": 0,
            "userid": auth_data.username,
            "password": hash_ps,
            "balance": 5000,
            "stock": [],
            "stock_display": [],
            "kakuhen": 0,
            "now_get": 0,
            "get": 0,
            "total": 0
        }
        user_db.dump()

        create_access_token(auth_data.username)

        user_db.dump()
        return Response(status_code=status.HTTP_201_CREATED)


@router.post("/users/login/",
             summary='log in',
             description='create access token',
             response_description='None',
             tags=["Auth"],
             responses={201: {"model": auth_token},
                        401: {"model": Message}})
async def get_access_token(auth_data: OAuth2PasswordRequestForm = Depends()):
    user_db.load()
    user_id = auth_data.username
    user_id_hash = str_hash(user_id)
    user_pw = str_hash(auth_data.password)

    if user_id_hash in user_db():
        if user_db()[user_id_hash]["password"] == user_pw:
            token = create_access_token(user_id)
            return JSONResponse(status_code=status.HTTP_201_CREATED,
                                content={"token_type": "bearer",
                                         "access_token": token})

    return Response(status_code=status.HTTP_401_UNAUTHORIZED)


def token_auth(token: str = Depends(oauth2_scheme)):
    user_db.load()
    try:
        payload = jwt.decode(token, KEY, ALGORITHM)

        user_id = payload["userid"]
        hash_user_id = str_hash(user_id)

        user_id = user_id if hash_user_id in user_db() else ""
        auth = False
        if datetime.utcnow().timestamp() < payload["exp"] and user_id != "":
            if user_db()[hash_user_id]["access_token"] == token:
                auth = True
        permission = user_db()[hash_user_id]["permission"] if auth else -1
        new_token = ""
        if auth:
            new_token = create_access_token(user_id)
            user_db()[hash_user_id]["access_token"] = new_token
            user_db.dump()
        return auth_info(user_id, auth, permission, new_token)
    except jose.exceptions.ExpiredSignatureError:
        return auth_info("", False, -1, "")


@router.delete("/user/delete")
def delete_account(response: Response, delete_id: str, auth: auth_info = Depends(token_auth)):
    if auth.auth is False:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    user_db.load()
    if str_hash(delete_id) not in user_db():
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    delete_user = user_db()[str_hash(delete_id)]
    if auth.permission < delete_user["permission"] or auth.user_id == delete_user["userid"]:
        user_db().pop(str_hash(delete_id))
        user_db.dump()
        json_resp = JSONResponse(status_code=status.HTTP_200_OK, content=delete_user)
        json_resp.set_cookie("access_token", auth.new_token, expires=datetime.utcnow() + timedelta(minutes=15))

        return json_resp
    else:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)


def set_token_cookie(new_token, response):
    response.set_cookie("access_token", new_token,
                        expires=str(datetime.utcnow() + timedelta(minutes=15)),
                        secure=True,
                        samesite=None)
    return response
