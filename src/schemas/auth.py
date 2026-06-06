from pydantic import BaseModel

from src.schemas.requests.auth import LoginRequest, SignUpRequest
from src.schemas.responses.auth import AuthMessageResponse, LoginResponse


class TokenRequest(BaseModel):
    access_token: str
    token_type: str = "bearer"

