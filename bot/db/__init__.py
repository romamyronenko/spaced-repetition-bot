from sqlalchemy import create_engine

DB_URI = "mysql+pymysql://roma:1@localhost/spaced_repetition"
engine = create_engine(DB_URI, echo=False, future=True)
