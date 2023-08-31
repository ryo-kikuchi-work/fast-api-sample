import random
from datetime import datetime, timedelta
from fastapi import Cookie, APIRouter, Form, Request, Depends
from fastapi import Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import status
from typing import Optional
from script.DB import json_db
from script.routers.auth import auth_info, set_token_cookie
from script.routers.auth import str_hash, token_auth
import copy

router = APIRouter()
templates = Jinja2Templates(directory="routers/page/")

user_db = json_db.DB("DB/users.json")


def make_play_data(user_data):
    user_data = copy.deepcopy(user_data)
    del user_data["permission"]
    del user_data["password"]
    return user_data


@router.get("/users/mypage",
            summary='mypage',
            description='Get User Data',
            response_description='OK',
            tags=["User"])
async def get_mypage(request: Request, access_token: Optional[str] = Cookie(None)):
    if access_token is None:
        return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)
    auth = token_auth(access_token)
    if not auth.auth:
        return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)
    user_db.load()
    if user_db()[str_hash(auth.user_id)]["balance"] <= 0:
        return Response(status_code=status.HTTP_423_LOCKED)
    if auth.auth:
        return set_token_cookie(auth.new_token,
                                templates.TemplateResponse("mypage.html",
                                                           {"request": request,
                                                            "user": make_play_data(user_db()[str_hash(auth.user_id)]),
                                                            }))

    return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)
