from fastapi import Cookie, APIRouter, Form, Request, Depends
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, Response
from fastapi import status
from typing import Optional
from script.DB import json_db
from script.routers.auth import auth_info, set_token_cookie
from script.routers.auth import str_hash, token_auth
import random

from script.routers.users import make_play_data

router = APIRouter()
templates = Jinja2Templates(directory="routers/page/")

user_db = json_db.DB("DB/users.json")


def calc_stock(num):
    if random.randrange(2) == 0 and num < 30:
        return "灰"
    if random.randrange(2) == 0 and num < 20:
        return "青"
    if random.randrange(2) == 0 and num < 10:
        return "緑"
    if random.randrange(2) == 0 and num < 2:
        return "赤"
    if random.randrange(2) == 0 and num < 1:
        return "金"
    return "白"


def select_staging(num):
    staging = dict()
    staging["riichi"] = random.randrange(30) == 0 or num < 20  # リーチ
    staging["alert"] = random.randrange(3) == 0 and num < 100  # アラート
    staging["effect"] = calc_stock(num)  # エフェクト
    staging["hot"] = random.randrange(2) == 0 and num < 10  # 激熱
    staging["continue"] = random.randrange(5) == 0 and staging["riichi"]  # 継続
    staging["lille"] = random.sample(range(1, 10), 3)  # リール
    staging["jackpot"] = num == 0
    if staging["riichi"]:
        staging["lille"][0] = staging["lille"][2]
    if num == 0:
        staging["lille"][1] = staging["lille"][0]
    return staging


@router.get("/users/try",
            summary='get slot result',
            description='slot API',
            response_description='result',
            tags=["Game"])
async def get_try(access_token: Optional[str] = Cookie(None)):
    if access_token is None:
        return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)
    auth = token_auth(access_token)
    if not auth.auth:
        return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)

    user_db.load()
    if len(user_db()[str_hash(auth.user_id)]["stock"]) <= 0:
        return set_token_cookie(auth.new_token, Response(status_code=status.HTTP_423_LOCKED))
    if auth.auth:
        result = user_db()[str_hash(auth.user_id)]["stock"].pop(0)
        user_db()[str_hash(auth.user_id)]["stock_display"].pop(0)
        user_db.dump()
        staging = select_staging(result)
        if staging["continue"]:
            num = random.randrange(result + 1)
            user_db()[str_hash(auth.user_id)]["stock"].insert(0, num)
            user_db()[str_hash(auth.user_id)]["stock_display"].insert(0, calc_stock(num))
        elif staging["jackpot"]:
            if user_db()[str_hash(auth.user_id)]["total"] == 0:
                user_db()[str_hash(auth.user_id)]["get"] = 200
            else:
                get_bonus = random.randrange(1, 20)
                get_bonus = random.randrange(1, get_bonus + 1)
                user_db()[str_hash(auth.user_id)]["get"] = 200 * random.randrange(1, get_bonus + 1)
                user_db()[str_hash(auth.user_id)]["kakuhen"] = 80 + random.randrange(2) * 40

        user_db.dump()
        return set_token_cookie(auth.new_token,
                                JSONResponse(
                                    {"user": make_play_data(user_db()[str_hash(auth.user_id)]),
                                     "result": staging}))

    return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/users/shot",
            summary='get shot result',
            description='slot API',
            response_description='result',
            tags=["Game"])
async def get_shot(access_token: Optional[str] = Cookie(None)):
    if access_token is None:
        return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)
    auth = token_auth(access_token)
    if not auth.auth:
        return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)

    user_db.load()
    if user_db()[str_hash(auth.user_id)]["balance"] <= 0:
        return set_token_cookie(auth.new_token, Response(status_code=status.HTTP_423_LOCKED))

    if auth.auth:
        is_hit = False
        if user_db()[str_hash(auth.user_id)]["get"] > 0:
            if user_db()[str_hash(auth.user_id)]["now_get"] > user_db()[str_hash(auth.user_id)]["get"]:
                user_db()[str_hash(auth.user_id)]["get"] = 0

            user_db()[str_hash(auth.user_id)]["now_get"] += 13
            user_db()[str_hash(auth.user_id)]["total"] += 13
            user_db()[str_hash(auth.user_id)]["balance"] += 13

        else:

            lot = random.randrange(30)
            if user_db()[str_hash(auth.user_id)]["kakuhen"] > 0:
                user_db()[str_hash(auth.user_id)]["kakuhen"] -= 1
                lot = random.randrange(2, 8)
            else:
                user_db()[str_hash(auth.user_id)]["now_get"] = 0
                user_db()[str_hash(auth.user_id)]["total"] = 0

            if lot < 2:
                user_db()[str_hash(auth.user_id)]["balance"] += random.randrange(4) + 2
            elif lot < 5:
                user_db()[str_hash(auth.user_id)]["balance"] += 1
                if len(user_db()[str_hash(auth.user_id)]["stock"]) < 5:
                    stock_temp = random.randrange(319)
                    if user_db()[str_hash(auth.user_id)]["kakuhen"] > 0:
                        stock_temp = random.randrange(98)
                    user_db()[str_hash(auth.user_id)]["stock"].append(stock_temp)
                    user_db()[str_hash(auth.user_id)]["stock_display"].append(calc_stock(stock_temp))
                    is_hit = True
            else:
                user_db()[str_hash(auth.user_id)]["balance"] -= 1
        user_db.dump()
        return set_token_cookie(auth.new_token,
                                JSONResponse(
                                    {"user": make_play_data(user_db()[str_hash(auth.user_id)]),
                                     "hit": is_hit
                                     }))

    return RedirectResponse("/", status_code=status.HTTP_401_UNAUTHORIZED)
