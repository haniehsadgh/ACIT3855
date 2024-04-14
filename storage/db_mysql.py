import functools
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mysql.connector 


MYSQL_DATABASE_URI = 'mysql+pymysql://user:Password@acit3855-kafla.eastus2.cloudapp.azure.com:3306/events'
#MYSQL_DATABASE_URI = 'mysql+pymysql://root:Password@127.0.0.1:3306/storage'
# DB_PATH = "sqlite:///traffic.db"
engine = create_engine(MYSQL_DATABASE_URI,pool_size=10, pool_recycle=3600, pool_pre_ping=True)

def make_session():
    return sessionmaker(bind=engine)()

def use_db_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = make_session()
        try:
            return func(session, *args, **kwargs)
        finally:
            session.close()

    return wrapper
