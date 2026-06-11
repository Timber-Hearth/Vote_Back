from pydantic import BaseModel
from datetime import datetime

from schemas.requests.PollGroup import OptionData, SinglePollData


class Response_PollGroup_Token(BaseModel):
    token : str
    title : str
    description : str
    is_closed : str
    created_at : str
    delete_after_hours : str
    is_public_result : str
    expire_at : str
    poll_data_list : list[SinglePollData]
