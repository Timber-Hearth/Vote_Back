from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.votes import vote_router
from src.api.v1.auth import auth_router
from src.api.v1.polls import poll_router

app = FastAPI()
app.include_router(router=auth_router, prefix="/auth", tags=["auth"])
app.include_router(router=poll_router, prefix="/polls", tags=["polls"])
app.include_router(router=vote_router, prefix="/vote", tags=["vote"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}