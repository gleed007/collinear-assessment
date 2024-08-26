from typing import List

from pydantic import BaseModel


class DatasetResponse(BaseModel):
  dataset_rows_count: int
  dataset_rows_per_page: int
  columns: List[str]
  rows: List[dict]

class ClusterData(BaseModel):
    label: str
    color: str
    x: List[float]
    y: List[float]

class ClusterGraphData(BaseModel):
    first_dataset: str
    second_dataset: str
    clusters: List[ClusterData]

class MatchingDataset(BaseModel):
   dataset_names: List['str']