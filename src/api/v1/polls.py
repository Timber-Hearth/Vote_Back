from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import GetCurrentUserFromToken
from src.models import User
from src.schemas.poll import CreatePollRequest
from src.services.poll_service import ServiceCreatePoll, ServiceGetPoll, ServiceGetOptionsFromPollID

poll_router = APIRouter()

@poll_router.post("/create")
def CreatePoll(request : CreatePollRequest, db : Session = Depends(get_db), current_user: User = Depends(GetCurrentUserFromToken)):
    result = ServiceCreatePoll(db = db, owner_id = current_user.id, request = request)
    return {"message" : "success", "data": result}

@poll_router.get("/{token}")
def GetPoll(token : str, db : Session = Depends(get_db)):
    poll_data = ServiceGetPoll(db, token)
    if not poll_data:
        return {"error": "Poll not found"}
    options = ServiceGetOptionsFromPollID(db, poll_data.id)
    return {"data" : poll_data, "options" : options}
