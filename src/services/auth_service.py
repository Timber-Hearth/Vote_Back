from sqlalchemy.orm import Session

from src.core.security import GetPasswordHash, VerifyPassword
from src.models import User


def ServiceSignUp(db: Session, login_id : str, password : str):
    exist_user = (
        db.query(User)
        .filter(User.login_id == login_id)
        .first()
    )
    if exist_user:
        raise Exception("User already exists")
    else:
        hash_password = GetPasswordHash(password)
        user = User(login_id=login_id, password_hash=hash_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

def ServiceLogin(db: Session, login_id: str, password: str):
    exist_user = (
        db.query(User)
        .filter(User.login_id == login_id)
        .first()
    )
    if exist_user and VerifyPassword(password, exist_user.password_hash):
        return exist_user
    else:
        return None