from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.exceptions.auth import AuthError
from src.core.security import CreateAccessToken
from src.schemas.auth import LoginRequest, SignUpRequest
from src.services.auth_service import ServiceLogin, ServiceSignUp

auth_router = APIRouter()

@auth_router.post("/login")
def Login(request: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    try:
        user = ServiceLogin(db, request.login_id, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    token = CreateAccessToken(
        {
            "sub" : user.login_id,
            "user_id" : user.id
        }
    )
    return {"access_token" : token, "token_type" : "bearer"}

@auth_router.post("/signup")
def SignUp(request: SignUpRequest, db: Annotated[Session, Depends(get_db)]):
    try:
        ServiceSignUp(db, request.login_id, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    return {"message" : "success"}
    