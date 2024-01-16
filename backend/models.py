from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel


Base = declarative_base()

class RowOrm(Base):
    __tablename__ ="binance_btcusdt_1m"
    timestamp = Column(DateTime, primary_key=True)
    open= Column(Float)
    high= Column(Float)
    low= Column(Float)
    close= Column(Float)
    volume= Column(Float)

class BacktestInput(BaseModel):
    freq: str
    anchor_period: str
    x: int
    vol_ratio: float
    tp: float
    sl: float