from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import CreateAccessToken
from src.schemas.auth import LoginRequest, SignUpRequest
from src.services.auth_service import ServiceLogin, ServiceSignUp

auth_router = APIRouter()

@auth_router.post("/login")
def Login(request: LoginRequest, db: Session = Depends(get_db)):
    user = ServiceLogin(
        db,
        request.login_id,
        request.password
    )
    if not user:
        raise HTTPException(
            status_code = 401,
            detail = "invalid"
        )
    token = CreateAccessToken(
        {
            "sub" : user.login_id,
            "user_id" : user.id
        }
    )
    return {"access_token" : token, "token_type" : "bearer"}

@auth_router.post("/signup")
def SignUp(request: SignUpRequest, db : Session = Depends(get_db)):
    user = ServiceSignUp(
        db,
        request.login_id,
        request.password
    )
    return {"message" : "success"}
    