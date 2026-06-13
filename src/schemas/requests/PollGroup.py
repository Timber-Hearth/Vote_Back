from datetime import datetime

from pydantic import BaseModel, field_validator

class OptionData(BaseModel):
    option_text : str
    
class ChangeTimeRequest(BaseModel):
    token : str
    add_hours : int
    
class SetPublicRequest(BaseModel):
    token : str
    is_public : bool

class SinglePollData(BaseModel):
    title : str
    description : str
    allow_multiple_choice : bool
    options : list[OptionData]

class Request_Create_PollGroup(BaseModel):
    title : str
    description : str
    created_at : str
    delete_after_hours : str
    is_public_result : bool
    expire_at : str
    poll_data_list : list[SinglePollData]
