from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.schemas.responses.common import RootResponse

from src.api.v1.auth import auth_router
from src.api.v1.poll_group import poll_group_router
from src.api.v1.vote import vote_router
from src.api.v1.migration import migration_router
from src.api.v1.qr import qr_router

app = FastAPI()

app.include_router(router=auth_router, prefix="/auth", tags=["auth"])
app.include_router(router=poll_group_router, prefix="/poll_group", tags=["poll_group"])
app.include_router(router=vote_router, prefix="/vote", tags=["vote"])
app.include_router(router=migration_router, prefix="/migration", tags=["migration"])
app.include_router(router=qr_router, prefix="/qr", tags=["qr"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=RootResponse)
def read_root():
    return {"Hello": "World"}