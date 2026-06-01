from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session

from src.services.poll_service import ServiceGetPoll
from src.core.database import get_db
from schemas.vote import VoteRequest

vote_router = APIRouter()

@vote_router.post("/{token}")
def Vote(token : str, request : VoteRequest, db : Session = Depends(get_db)):
    poll_data = ServiceGetPoll(db, token)

    pass