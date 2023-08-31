import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from routers import users, auth, game
from script.DB import json_db

app = FastAPI()

templates = Jinja2Templates(directory="routers/page/")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(game.router)

user_db = json_db.DB("DB/users.json")


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register",
         summary='Sign In',
         description='show sign in page.',
         response_description='html',
         tags=["auth"])
def sign_in(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login",
         summary='log In',
         description='show log in page.',
         response_description='html',
         tags=["auth"])
def log_in(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
