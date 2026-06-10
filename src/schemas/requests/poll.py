from pydantic import BaseModel, field_validator


class CreatePollRequest(BaseModel):
    title: str
    description: str
    options: list[str]

    poll_group_id: int
    allow_multiple_choice: bool = False

    @field_validator("options")
    @classmethod
    def ValidateOptions(cls, value: list[str]) -> list[str]:
        normalized_options = [option.strip() for option in value if option.strip()]
        if len(normalized_options) < 2:
            raise ValueError("options must contain at least 2 non-empty values")
        return normalized_options