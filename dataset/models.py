from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base


class Impact(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class DatasetInfo(Base):
    __tablename__ = 'dataset_info'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    author = Column(String)
    created_at = Column(DateTime(timezone=True))
    last_modified = Column(DateTime(timezone=True))
    downloads = Column(Integer)
    likes = Column(Integer)
    size_category = Column(String)
    impact = Column(String)

    followed_by = relationship("FollowedDataset", back_populates="dataset")


class FollowedDataset(Base):
    __tablename__ = 'followed_datasets'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    dataset_id = Column(Integer, ForeignKey('dataset_info.id'), primary_key=True)
    followed_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with users
    user = relationship("UserModel", back_populates="followed_datasets")

    # Relationship with datasets
    dataset = relationship("DatasetInfo", back_populates="followed_by")

class ClusterGraph(Base):
    __tablename__ = 'cluster_graph'

    id = Column(Integer, primary_key=True, index=True)
    first_dataset = Column(String)
    second_dataset = Column(String)
    clusters = Column(JSON)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("UserModel", back_populates="cluster_graphs")

