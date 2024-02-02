__all__ = ["db_manager"]

import os

from sqlalchemy import create_engine

from .dbmanager import DBManager
from .schema import Base

_DB_URI = os.getenv("DB_URI", "sqlite://")
_engine = create_engine(_DB_URI, echo=False, future=True)
Base.metadata.create_all(_engine)
db_manager = DBManager(_engine)
