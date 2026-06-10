from sqlalchemy.orm import Session

from src.schemas.requests.PollGroup import CreatePollGroupRequest
from src.models import PollGroup


def Repo_CreatePollGroup(db: Session, request: CreatePollGroupRequest, current_user) -> PollGroup:
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