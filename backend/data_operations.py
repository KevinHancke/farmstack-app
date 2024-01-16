from fastapi import BackgroundTasks
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from get_data import get_new_rows, append_new_rows
from models import RowOrm
from database import engine
import pandas as pd
from tqdm import tqdm

async def fetch_data(engine, db: Session, background_tasks=BackgroundTasks):
    try:
        items = db.query(RowOrm).order_by(RowOrm.timestamp.desc()).limit(100).all()
        items = reversed(items)
        data = [
            {
                "time": int(pd.to_datetime(item.timestamp).timestamp()),
                "open": round(item.open, 2),
                "high": round(item.high, 2),
                "low": round(item.low, 2),
                "close": round(item.close, 2),
            } 
            for item in tqdm(items)
        ]
        print(f"Fetched data from sql sum {len(data)}")
        return data
    
    except Exception as e:
        raise e

async def update_data(engine, background_tasks: BackgroundTasks):
    # Implement logic for fetching and appending new rows
    get_new_rows(engine)
    print("getting new rows from binance")
    append_new_rows(engine)
    print("appending the new rows")
    # Add background task to re-run after 1 hours
    background_tasks.add_task(update_data, engine, background_tasks, delay=timedelta(hours=1))
    print("we ought to have scheduled/running the the collection and appending of new rows")