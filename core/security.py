from datetime import datetime, timedelta

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from auth.models import UserModel
from core.config import get_settings
from core.database import get_db

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(data,  expiry: timedelta):
    payload = data.copy()
    expire_in = datetime.utcnow() + expiry
    payload.update({"exp": expire_in})
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def create_refresh_token(data):
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_token_payload(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        print(e)
        return None
    return payload

def get_current_user(token, db):
    payload = get_token_payload(token=token)
    if not payload or not isinstance(payload,dict):
        return None

    user_id = payload.get('id', None)
    if not user_id:
        return None

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    return user

def get_user_by_bearer_token(Authorization: str = Header(), db: Session = Depends(get_db)):
    token = Authorization.replace("Bearer ", "")
    return get_current_user(token=token, db=db)