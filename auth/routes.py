from fastapi import APIRouter, Depends, Header, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth.models import UserModel
from auth.responses import TokenResponse, UserResponse
from auth.schemas import CreateUserRequest
from auth.services import (
    create_user_account,
    get_refresh_token,
    get_token,
)
from core.database import get_db
from core.security import get_current_user
from dataset.models import DatasetInfo, FollowedDataset

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

def get_user_by_bearer_token(Authorization: str = Header(), db: Session = Depends(get_db)):
    token = Authorization.replace("Bearer ", "")
    return get_current_user(token=token, db=db)

@router.post('', status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserRequest, db: Session = Depends(get_db)):
    await create_user_account(data=data, db=db)
    payload = {"message": "User account has been succesfully created."}
    return JSONResponse(content=payload)

@router.post("/token", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def authenticate_user(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await get_token(data=data, db=db)

@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def refresh_access_token(refresh_token: str = Header(), db: Session = Depends(get_db)):
    return await get_refresh_token(token=refresh_token, db=db)

@user_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_detail(user: UserModel = Depends(get_user_by_bearer_token)):
    return user
    
@user_router.get("/datasets/followed", status_code=status.HTTP_200_OK)
async def get_followed_datasets(user: UserModel = Depends(get_user_by_bearer_token), db:Session = Depends(get_db)):
    return db.query(DatasetInfo).join(FollowedDataset).filter(FollowedDataset.user_id == user.id).all()