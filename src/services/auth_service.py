from sqlalchemy.orm import Session

from src.exceptions.auth import InvalidCredentialsError, UserAlreadyExistsError
from src.core.security import GetPasswordHash, VerifyPassword
from src.repositories.user_repository import CreateUser, GetUserByLoginID


def ServiceSignUp(db: Session, login_id : str, password : str):
    exist_user = GetUserByLoginID(db, login_id)
    if exist_user:
        raise UserAlreadyExistsError()

    hash_password = GetPasswordHash(password)
    return CreateUser(db, login_id, hash_password)

def ServiceLogin(db: Session, login_id: str, password: str):
    exist_user = GetUserByLoginID(db, login_id)
    if exist_user and VerifyPassword(password, exist_user.password_hash):
        return exist_user

    raise InvalidCredentialsError()
