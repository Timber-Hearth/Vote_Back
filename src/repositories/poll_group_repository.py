import secrets

from src.core.pubsub import PubSub
from src.models.poll import Poll

from src.schemas.requests.PollGroup import Request_Create_PollGroup
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import PollOption, PollGroup

def Repo_OwnerCheker(db, user_id, poll_group_id):
    group = db.query(PollGroup).filter(PollGroup.id == poll_group_id).first()
    if group is None:
          return False
    if group.owner_id != user_id:
          return False
    return True

def Repo_OwnerCheckerByToken(db, user_id, token):
    group = db.query(PollGroup).filter(PollGroup.qr_token == token).first()
    if group is None:
          return False
    if group.owner_id != user_id:
          return False
    return True

def Repo_GetPollGroupByToken(token, db):
    poll_group = db.query(PollGroup).filter(PollGroup.qr_token == token).first()
    return poll_group

def Repo_GetPollSettingsByToken(token, db):
    poll_group = db.query(PollGroup).filter(PollGroup.qr_token == token).first()
    if poll_group is None:
          return None
    return {
          "delete_after_hours": poll_group.delete_after_hours,
          "is_public_result": poll_group.is_public_result,
          "expire_at": poll_group.expire_at,
          "is_closed": poll_group.is_closed
     }


def Repo_GetPollGroupData(db: Session, token: str) -> PollGroup | None:
     return db.query(PollGroup).filter(PollGroup.qr_token == token).first()

def Repo_GetPollDataFromPollGroupId(db: Session, group_id: str):
     return db.query(Poll).where(Poll.group_id == group_id).all()

def Repo_GetOptionsFromPollId(db: Session, id: str):
     return db.query(PollOption).where(PollOption.poll_id == id).all()

def Repo_CreatePollGroup(db: Session, owner_id: int, data: Request_Create_PollGroup) -> bool:
     try:
          qr_token = secrets.token_urlsafe(16)
          new_poll_group = PollGroup(
               owner_id=owner_id,
               title=data.title,
               description=data.description,
               qr_token=qr_token,
               created_at=data.created_at,
               delete_after_hours=data.delete_after_hours,
               is_public_result=data.is_public_result,
               expire_at=data.expire_at
          )
          db.add(new_poll_group)
          db.commit()
          db.refresh(new_poll_group)
          for poll_data in data.poll_data_list:
               new_poll = Poll(
                    group_id=new_poll_group.id,
                    title=poll_data.title,
                    description=poll_data.description,
                    allow_multiple_choice=poll_data.allow_multiple_choice
               )
               db.add(new_poll)
               db.commit()
               db.refresh(new_poll)
               counter = 0
               for option in poll_data.options:
                    new_option = PollOption(
                         poll_id=new_poll.id,
                         option_text=option.option_text,
                         poll_group_qr=new_poll_group.qr_token,
                         display_order=counter
                    )
                    db.add(new_option)
                    db.commit()
                    db.refresh(new_option)
                    counter += 1
          pub_sub = PubSub()
          pub_sub.PublishManage("create_poll_group", {"qr_token": qr_token})
     except Exception as e:
          db.rollback()
          print(e)
          return False
     return True

def Repo_AddDeleteTime(db: Session, token: str, add_hours: int) -> bool:
     try:
          poll_group = db.query(PollGroup).filter(PollGroup.qr_token == token).first()
          if poll_group is None:
               return False
          poll_group.delete_after_hours += add_hours
          db.commit()
     except Exception as e:
          db.rollback()
          print(e)
          return False
     return True

def Repo_SetPublic(db: Session, token: str, is_public: bool) -> bool:
     try:
          poll_group = db.query(PollGroup).filter(PollGroup.qr_token == token).first()
          if poll_group is None:
               return False
          poll_group.is_public_result = is_public
          db.commit()
     except Exception as e:
          db.rollback()
          print(e)
          return False
     return True

def Repo_EditExpireTime(db: Session, token: str, add_hours: int) -> bool:
     try:
          poll_group = db.query(PollGroup).filter(PollGroup.qr_token == token).first()
          if poll_group is None:
               return False
          poll_group.expire_at = func.date_add(poll_group.expire_at, func.interval(add_hours, 'hour'))
          db.commit()
     except Exception as e:
          db.rollback()
          print(e)
          return False
     return True