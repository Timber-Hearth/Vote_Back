from fastapi import FastAPI

from api.v1.auth import auth_router

app = FastAPI()
app.include_router(router=auth_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}