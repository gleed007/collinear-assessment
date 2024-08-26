from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(100))
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    followed_datasets = relationship("FollowedDataset", back_populates="user")

    cluster_graphs = relationship("ClusterGraph", back_populates="user")