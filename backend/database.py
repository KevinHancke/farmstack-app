from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQL_DATABASEURL = "sqlite:///./btc.db"

engine = create_engine(
    SQL_DATABASEURL, connect_args={"check_same_thread":False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)