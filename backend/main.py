from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime
from data_operations import fetch_data, update_data
import asyncio

from models import RowOrm, BacktestInput
from database import engine, SessionLocal

from backtest import backtest
from typing import Dict, Any
import json

RowOrm.metadata.create_all(bind=engine)

async def run_background_tasks():
    background_tasks = BackgroundTasks()
    await update_data(engine, background_tasks)

async def startup_event():
    # Schedule the background task on application startup
    await run_background_tasks()

"""@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_background_tasks()
    db = SessionLocal()
    try:
        yield db
    finally: db.close()"""

"""app = FastAPI(lifespan=lifespan)"""

app = FastAPI()

origins = ["http://localhost:3000", "http://localhost:3001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""@app.get("/")
async def get_sql_table(request: Request, background_tasks: BackgroundTasks):
    async with lifespan(app) as db:
        try:
            data = await fetch_data(engine, db, background_tasks)
            return JSONResponse(content=data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")"""
        
#For backtesting with a post request      
def run_backtest_logic(backtest_input: Dict[str, Any]):
    print(json.dumps(backtest_input, indent=2))
    result = backtest(
        backtest_input['freq'],
        backtest_input['anchor_period'],
        int(backtest_input['x']),
        float(backtest_input['vol_ratio']),
        float(backtest_input['tp']),
        float(backtest_input['sl']),
    )
    """data = [
            {
                "amount of trades": result[0],
                "winrate": result[1],
                "cumulative pnl %": result[2],
            }]"""
    
    return result

@app.post("/backtest", response_model=Dict[str, Any])
async def run_backtest(backtest_input: Dict[str, Any]):
    try:
        result = run_backtest_logic(backtest_input)
        return {"result": result.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))