from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator

MAX_BCRYPT_PASSWORD_BYTES = 72


class SignUpRequest(BaseModel):
    login_id: str
    password: str
    expire_at: datetime

    @model_validator(mode="before")
    @classmethod
    def NormalizeLoginIDAlias(cls, values):
        if not isinstance(values, dict):
            return values
        if values.get("login_id"):
            return values

        for key in ("username", "email", "user_id"):
            alias_value = values.get(key)
            if alias_value:
                values["login_id"] = alias_value
                break
        return values

    @field_validator("login_id")
    @classmethod
    def NormalizeLoginID(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("login_id must not be empty")
        return value

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

    @model_validator(mode="before")
    @classmethod
    def NormalizeLoginIDAlias(cls, values):
        if not isinstance(values, dict):
            return values
        if values.get("login_id"):
            return values

        for key in ("username", "email", "user_id"):
            alias_value = values.get(key)
            if alias_value:
                values["login_id"] = alias_value
                break
        return values

    @field_validator("login_id")
    @classmethod
    def NormalizeLoginID(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("login_id must not be empty")
        return value

    @field_validator("password")
    @classmethod
    def ValidatePasswordByteLength(cls, value: str) -> str:
        if len(value.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
            raise ValueError(
                f"password must be {MAX_BCRYPT_PASSWORD_BYTES} bytes or less in UTF-8"
            )
        return value

