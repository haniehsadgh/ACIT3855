import functools
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = "sqlite:////data/stats.db"

#install mysqclient
#use disable_exisiting_loggers: false in YAML conf
#should be able to use .create_all to create your schema
#use mysql://user:pass@host:port/database for database string

engine = create_engine(DB_PATH)

def make_session():
    return sessionmaker(bind=engine) ()

def use_db_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = make_session()
        try:
            return func(session, *args, **kwargs)
        finally:
            session.close()
    
    return wrapper
