from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from db.schema import Card, Base

engine = create_engine("sqlite:///db.db")
base = declarative_base()
db_session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def add_commit_flush(session, *args):
    for obj in args:
        session.add(obj)
    session.commit()
    session.flush()


def test_card():
    card = Card(front_side="1", back_side="2", owner=1)
    with Session(engine) as session:
        add_commit_flush(session, card)

        assert card.id is not None
