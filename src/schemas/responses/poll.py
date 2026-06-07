from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreatePollDataResponse(BaseModel):
    token: str
    qr_token: str


class CreatePollResponse(BaseModel):
    message: str
    data: CreatePollDataResponse


class PollPublicDataResponse(BaseModel):
    owner_id: int
    title: str
    description: str | None = None
    is_public_result: bool
    is_closed: bool
    created_at: datetime
    expire_at: datetime | None = None
    allow_multiple_choice: bool
    delete_after_hours: int
    qr_token: str


class PollOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    poll_id: UUID
    option_text: str
    display_order: int
    created_at: datetime


class PollDetailResponse(BaseModel):
    data: PollPublicDataResponse
    options: list[PollOptionResponse]


class PollListItemResponse(BaseModel):
    title: str
    description: str | None = None
    is_closed: bool
    allow_multiple_choice: bool
    delete_after_hours: int
    is_public_result: bool
    created_at: datetime
    expire_at: datetime | None = None
    qr_token: str


class PollListResponse(BaseModel):
    data: list[PollListItemResponse]


class PollMessageResponse(BaseModel):
    message: str


class PollResultOptionResponse(BaseModel):
    option_id: int
    option_text: str
    count: int


class PollResultPollDataResponse(BaseModel):
    owner_id: int
    title: str
    description: str | None = None
    is_public_result: bool
    my_poll: bool
    is_closed: bool
    allow_multiple_choice: bool
    expire_at: datetime | None = None
    created_at: datetime
    qr_token: str


class PollResultDataResponse(BaseModel):
    poll_data: PollResultPollDataResponse
    options: list[PollResultOptionResponse]


class PollResultDetailResponse(BaseModel):
    data: PollResultDataResponse

