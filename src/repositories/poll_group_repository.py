from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models import PollOption, PollGroup
from src.models import Poll




def Repo_GetPollGroupData(db: Session, token: str) -> PollGroup:
     return db.query(PollGroup).where(PollGroup.qr_token == token).first()
