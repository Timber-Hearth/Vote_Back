from datetime import datetime
from sqlalchemy.orm import Session
from src.models import User, Polls
from src.repositories.id_allocator import AllocateNextBigIntIds


def GetUserByLoginID(db: Session, login_id: str):
	return db.query(User).filter(User.login_id == login_id).first()


def CreateUser(db: Session, login_id: str, password_hash: str, expire_date: datetime):
	user_id = AllocateNextBigIntIds(db, User, count=1)[0]
	user = User(id=user_id, login_id=login_id, password_hash=password_hash, expire_date=expire_date)
	db.add(user)
	try:
		db.commit()
	except Exception:
		db.rollback()
		raise
	db.refresh(user)
	return user
