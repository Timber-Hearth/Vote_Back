from schemas.requests.PollGroup import Request_Create_PollGroup
from sqlalchemy.orm import Session

from src.models import PollOption, PollGroup
from src.models import Poll




def Repo_GetPollGroupData(db: Session, token: str) -> type[PollGroup] | None:
     return db.query(PollGroup).where(PollGroup.qr_token == token).first()

def Repo_GetPollDataFromPollGroupId(db: Session, group_id: str):
     return db.query(Poll).where(Poll.group_id == group_id).all()

def Repo_GetOptionsFromPollId(db: Session, id: str):
     return db.query(PollOption).where(PollOption.poll_id == id).all()

def Repo_CreatePollGroup(db: Session, owner_id: int, data: Request_Create_PollGroup) -> bool:
     try:
          new_poll_group = PollGroup(
               owner_id=owner_id,
               title=data.title,
               description=data.description,
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

               for option in poll_data.options:
                    new_option = PollOption(
                         poll_id=new_poll.id,
                         option_text=option.option_text,
                         display_order=option.display_order
                    )
                    db.add(new_option)
                    db.commit()
                    db.refresh(new_option)
     except Exception as e:
          db.rollback()
          print(e)
          return False
     return True