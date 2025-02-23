from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, BigInteger
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow) 