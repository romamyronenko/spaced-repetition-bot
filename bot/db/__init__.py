from sqlalchemy import create_engine

from .dbmanager import DBManager
from .schema import Base

DB_URI = "mysql+pymysql://root:1@mysql/spaced_repetition"
engine = create_engine(DB_URI, echo=False, future=True)
Base.metadata.create_all(engine)
db_manager = DBManager(engine)
