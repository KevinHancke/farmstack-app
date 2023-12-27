from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime

from models import RowOrm
from database import engine, SessionLocal

from get_data import get_new_rows, append_new_rows

RowOrm.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["http://localhost:3000", "http://localhost:3001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Access the SQL db

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: db.close()

async def fetch_data(request: Request, db: Session=Depends(get_db)):
    try:
        get_new_rows(engine)
        append_new_rows(engine)

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
            for item in items
        ]

        return JSONResponse(content = data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/")
async def get_sql_table(request: Request, db: Session = Depends(get_db)):
    return await fetch_data(request, db)

@app.get("/sql_data")
async def get_sql_table(request: Request, db: Session = Depends(get_db)):
    return await fetch_data(request, db)

#Todo scheduler routes to be used with MongoDB Motor for the scheduler of backtests.

"""@app.get("/")
def read_root():
    return {"Hello World"}

@app.get("/api/todo")
async def get_todo():
    return 1

@app.get("/api/todo{id}")
async def get_todo_by_id(id):
    return 1

@app.post("/api/todo")
async def post_todo(todo):
    return 1

@app.put("/api/todo{id}")
async def put_todo(id, data):
    return 1

@app.delete("/api/todo{id}")
async def delete_todo(id):
    return 1"""