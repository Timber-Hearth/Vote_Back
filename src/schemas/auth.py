from pydantic import BaseModel

class SignUpRequest(BaseModel):
    login_id: str
    password: str
    
class LoginRequest(BaseModel):
    login_id: str
    password: str
    
class TokenRequest(BaseModel):
    access_token: str
    token_type: str = "bearer"