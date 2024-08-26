

from datetime import datetime

import numpy as np
import pandas as pd
import requests
from datasets import concatenate_datasets, load_dataset
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from huggingface_hub.hf_api import DatasetFilter, HfApi
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

from core.config import Settings
from dataset.models import ClusterGraph, DatasetInfo, FollowedDataset


# deepset/prompt-injections , teven/prompted_examples

async def get_dataset_by_name(dataset_name: str, offset:int, limit:int):
  base_url = Settings().DATASET_API_URL
  metadata_url = base_url + "splits?dataset={}"
  metadata = requests.get(metadata_url.format(dataset_name)).json()
  if len(metadata["splits"]) == 0:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
  
  split, config = metadata["splits"][0]["split"], metadata["splits"][0]["config"]
  request_url = base_url + "rows?dataset={}&config={}&split={}&offset={}&length={}"
  request_url = request_url.format(dataset_name, config, split, offset, limit)
  res = requests.get(request_url)
  if res.status_code != status.HTTP_200_OK:
      raise HTTPException(status_code=res.status_code, detail=res.json())
  res = res.json()
  return transform(res['features'],res['rows'], res['num_rows_total'])


def transform(features, rows, total_rows):
  cols = [feat["name"] for feat in features]
  records = [r["row"] for r in rows]
  return {
     "dataset_rows_count": total_rows,
     "dataset_rows_per_page": 100,
     "columns": cols,
     "rows": records
  }

async def follow_dataset_by_id(dataset_id: int, user_id: int, db):
  try:
      dataset = db.query(DatasetInfo).filter(DatasetInfo.id == dataset_id).first()
      if not dataset:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
      
      existing_followed_dataset = db.query(FollowedDataset).filter(
          FollowedDataset.user_id == user_id,
          FollowedDataset.dataset_id == dataset_id
      ).first()
      if existing_followed_dataset:
          raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already following this dataset")
      
      followed_dataset = FollowedDataset(
          user_id=user_id,
          dataset_id=dataset.id,
          followed_at=datetime.utcnow()
      )
      db.add(followed_dataset)
      db.commit()
      return {"message": "Dataset followed successfully"}
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Failed to follow dataset: {str(e)}")
  

async def get_compatible_datasets_by_name(dataset_name: str):
  api = HfApi()

  ds = list(api.list_datasets(filter= DatasetFilter(dataset_name)))[0]

  task_categories = []
  task_ids = []

  for item in ds.tags:
      if item.startswith('task_categories:'):
          task_categories.append(item.split(':')[1])
      elif item.startswith('task_ids:'):
          task_ids.append(item.split(':')[1])
     
  matching_ds = list(api.list_datasets(filter= DatasetFilter(task_categories=task_categories,task_ids=task_ids)))[:11]
  ds_names = [info.id for info in matching_ds]

  return {'dataset_names': ds_names}

def get_dataset(dataset: str):
  base_url = Settings().DATASET_API_URL
  metadata_url = base_url + "splits?dataset={}"
  metadata = requests.get(metadata_url.format(dataset)).json()    
  split = metadata["splits"][0]["split"]
  ds = load_dataset(dataset, split=split)
  return ds

def combine_dataset_and_perform_k_means_clustering(first_dataset_name: str, second_dataset_name: str, user_id: int, db): 
    print("combining datasets")
    ds1 = get_dataset(first_dataset_name)
    ds2 = get_dataset(second_dataset_name)

    dataset = concatenate_datasets([ds1,ds2])
    df = pd.DataFrame(dataset)

    sample_size = 10000 if df.size > 10000 else df.size
    df = df.sample(n=sample_size, random_state=49)

    # TF-IDF vectorization
    # print(df.dtypes)
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(df['text'])
    print("clustering datasets")
    # # K-means clustering
    num_clusters = 5  # Adjust the number of clusters as needed
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)
    labels = kmeans.labels_

    # Dimensionality reduction for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X.toarray())
    print("clustering done, seeding db")
    data = {}
    for i in range(num_clusters):
        cluster_data = {
            'label': f'Cluster {i}',
            'color': f'rgba({np.random.randint(0, 256)}, {np.random.randint(0, 256)}, {np.random.randint(0, 256)}, 0.8)',
            'x': X_pca[labels == i, 0].tolist(),
            'y': X_pca[labels == i, 1].tolist()
        }
        data[i] = cluster_data
    
    new_graph = ClusterGraph(
       first_dataset=first_dataset_name,
       second_dataset= second_dataset_name,
       clusters= data,
       user_id = user_id
    )
    db.add(new_graph) 
    db.commit()

    print("db record added")