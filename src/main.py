from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.auth import auth_router

app = FastAPI()
app.include_router(router=auth_router, prefix="/auth", tags=["auth"])
app.include_router(router=poll_group_router, prefix="/poll", tags=["poll"])


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