from pydantic import BaseModel, field_validator


class CreatePollRequest(BaseModel):
    title : str
    description : str | None = None
    options : list[str]
    
    allow_multiple_choice : bool = False
    delete_after_hours : int = 24
    is_public_result : bool = False

    @field_validator("options")
    @classmethod
    def ValidateOptions(cls, value: list[str]) -> list[str]:
        normalized_options = [option.strip() for option in value if option.strip()]
        if len(normalized_options) < 2:
            raise ValueError("options must contain at least 2 non-empty values")
        return normalized_options

    @field_validator("delete_after_hours")
    @classmethod
    def ValidateDeleteAfterHours(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("delete_after_hours must be greater than 0")
        return value

