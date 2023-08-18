from fastapi import Cookie, APIRouter, Form, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import status
from typing import Optional
from script.DB import json_db
from script.routers.auth import auth_info
from script.routers.room import token_auth
from script.routers.auth import str_hash

router = APIRouter()
templates = Jinja2Templates(directory="routers/page/")

user_db = json_db.DB("DB/users.json")


@router.get("/users/mypage",
            summary='mypage',
            description='Get User Data',
            response_description='OK',
            tags=["User"])
async def get_mypage(request: Request, access_token: Optional[str] = Cookie(None)):
    user_db.load()
    if access_token is None:
        return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)
    auth = token_auth(access_token)
    if auth.auth:
        return templates.TemplateResponse("mypage.html",
                                          {"request": request, "user": user_db()[str_hash(auth.user_id)]})

    return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)
