from fastapi import APIRouter, BackgroundTasks, Depends, Query, status, Request

# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth.models import UserModel
from core.database import get_db
from core.security import get_user_by_bearer_token
from dataset.models import ClusterGraph, DatasetInfo
from dataset.responses import DatasetResponse, MatchingDataset, ClusterGraphData
from dataset.services import (
    combine_dataset_and_perform_k_means_clustering,
    follow_dataset_by_id,
    get_compatible_datasets_by_name,
    get_dataset_by_name,
)

router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
    responses={404: {"description": "Not found"}},
)

@router.get('', status_code=status.HTTP_200_OK)
async def get_datasets(db: Session = Depends(get_db)):
    datasets = db.query(DatasetInfo).all()
    return datasets

@router.get('/{dataset_id:int}/follow', status_code=status.HTTP_200_OK)
async def follow_dataset(dataset_id: int, user: UserModel = Depends(get_user_by_bearer_token), db: Session = Depends(get_db)):
    return await follow_dataset_by_id(dataset_id, user.id, db)

@router.get('/compatible/{dataset_name:path}', status_code=status.HTTP_200_OK, response_model=MatchingDataset)
async def get_compatible_datasets(dataset_name: str):
    return await get_compatible_datasets_by_name(dataset_name)

@router.post('/combine', status_code=status.HTTP_202_ACCEPTED)
async def combine_datasets(request: Request,  background_tasks: BackgroundTasks, user: UserModel = Depends(get_user_by_bearer_token), db: Session= Depends(get_db)):
    data = await request.json()
    background_tasks.add_task(combine_dataset_and_perform_k_means_clustering, data["first_dataset_name"], data["second_dataset_name"], user.id, db)
    return {"message": "Combining datasets and performing k-means clustering"}

@router.get("/combined-datasets", status_code=status.HTTP_200_OK, response_model=ClusterGraphData)
async def get_combined_datasets(user: UserModel = Depends(get_user_by_bearer_token), db: Session = Depends(get_db)):
    combined_datasets = db.query(ClusterGraph).filter(ClusterGraph.user_id == user.id).all()
    return combined_datasets

@router.get('/{dataset_name:path}', status_code=status.HTTP_200_OK, response_model=DatasetResponse)
async def get_dataset(dataset_name: str, offset:int = Query(1, ge=0), limit:int = Query(100, ge=0)):
    return await get_dataset_by_name(dataset_name=dataset_name, offset=offset, limit=limit)