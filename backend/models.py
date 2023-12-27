from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

#Unused imports relevant to pydantic types
"""from typing import List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, constr"""

Base = declarative_base()

class RowOrm(Base):
    __tablename__ ="binance_btcusdt_1m"
    timestamp = Column(DateTime, primary_key=True)
    open= Column(Float)
    high= Column(Float)
    low= Column(Float)
    close= Column(Float)
    volume= Column(Float)

"""class Row(BaseModel):
    __tablename__="btc_1m"
    Datetime: datetime
    Open: float
    High: float
    Low: float
    Close: float
    Volume: float"""


#Class for the scheduler of tasks to be used with MongoDB & Motor
"""class Todo(BaseModel):
    title: str
    description: str"""