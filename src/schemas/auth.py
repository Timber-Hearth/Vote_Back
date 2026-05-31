from pydantic import BaseModel, field_validator

MAX_BCRYPT_PASSWORD_BYTES = 72

class SignUpRequest(BaseModel):
    login_id: str
    password: str

    @field_validator("password")
    @classmethod
    def ValidatePasswordByteLength(cls, value: str) -> str:
        if len(value.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
            raise ValueError(
                f"password must be {MAX_BCRYPT_PASSWORD_BYTES} bytes or less in UTF-8"
            )
        return value
    
class LoginRequest(BaseModel):
    login_id: str
    password: str

    @field_validator("password")
    @classmethod
    def ValidatePasswordByteLength(cls, value: str) -> str:
        if len(value.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
            raise ValueError(
                f"password must be {MAX_BCRYPT_PASSWORD_BYTES} bytes or less in UTF-8"
            )
        return value
    
class TokenRequest(BaseModel):
    access_token: str
    token_type: str = "bearer"