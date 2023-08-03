import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from routers import users, auth

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "hello, world!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
