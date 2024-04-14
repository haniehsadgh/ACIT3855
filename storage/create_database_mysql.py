# from models import Base
# from sqlalchemy import create_engine

# # Replace 'mysql+mysqlconnector' with your preferred MySQL dialect (e.g., 'mysql+pymysql')
# # Update 'username', 'password', 'host', 'port', and 'database_name' with your MySQL configuration
# MYSQL_DATABASE_URI = 'mysql+mysqlconnector://username:password@host:port/database_name'
# engine = create_engine(MYSQL_DATABASE_URI)

# def create_tables():
#     Base.metadata.create_all(engine)

# def drop_tables():
#     Base.metadata.drop_all(engine)

# if __name__ == "__main__":
#     create_tables()


from models_mysql import Base
from db_mysql import engine

def create_tables():
    Base.metadata.create_all(engine)


def drop_tables():
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    create_tables()