from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel


class auth_post(BaseModel):
    id: str
    pw: str


router = APIRouter()


@router.post("/users/login/",
             summary='login',
             description='create access token',
             response_description='None',
             tags=["Auth"])
async def post_login_info(auth_data: OAuth2PasswordRequestForm = Depends()):
    return {auth_data.password}


@router.get("/users/login/",
            summary='login',
            description='get access token',
            response_description='None',
            tags=["Auth"])
async def get_access_token():
    pass
