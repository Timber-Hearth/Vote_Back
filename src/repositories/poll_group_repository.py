from sqlalchemy.orm import Session

from src.models import PollOption, PollGroup
from src.models import Poll




def Repo_GetPollGroupData(db: Session, token: str) -> type[PollGroup] | None:
     return db.query(PollGroup).where(PollGroup.qr_token == token).first()

def Repo_GetPollDataFromPollGroupId(db: Session, group_id: str):
     return db.query(Poll).where(Poll.group_id == group_id).all()

def Repo_GetOptionsFromPollId(db: Session, id: str):
     return db.query(PollOption).where(PollOption.poll_id == id).all()

def Repo_CreatePollGroup(db: Session, owner_id: int) -> PollGroup: