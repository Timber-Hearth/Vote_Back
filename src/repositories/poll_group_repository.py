from sqlalchemy.orm import Session

from src.models import PollGroup
from src.schemas.requests.PollGroup import CreatePollGroupRequest
from src.models import Polls


def Repo_CreatePollGroup(db: Session, request: CreatePollGroupRequest, current_user) -> Polls:
    try:
        poll_group = PollGroup(
            title=request.title,
            owner_id=current_user.id,
            description=request.description,
            is_public_result=request.is_public_result,
            is_closed=False,
            created_at=request.create_at,
            expire_at=request.expire_at,
            delete_after_hours=request.delete_after_hours
        )
        db.add(poll_group)

    except Exception as e:
        db.rollback()
        print(e)
        return None
    db.commit()
    return poll_group

def Repo_GetPollGroupByToken(db: Session, token: str) -> PollGroup:
    try:
        poll_group = db.query(PollGroup).where(PollGroup.qr_token == token).first()
        return poll_group
    except Exception as e:
        print(e)
        return None

def Repo_GetPollListByToken(db: Session, token: str) -> list[Polls]:
    try:
        token_owner_id = Repo_GetPollGroupByToken(db=db, token=token).id
        polls = db.query(Polls).where(Polls.group_id == token_owner_id).all()
        return polls
    except Exception as e:
        print(e)
        return []

