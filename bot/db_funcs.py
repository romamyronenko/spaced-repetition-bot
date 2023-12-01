from sqlalchemy import select
from sqlalchemy.orm import Session

from db import engine
from db.schema import Card


def remove_card_from_db(front):
    with Session(engine) as session:
        stmt = select(Card).where(Card.front_side == front)
        card = session.scalars(stmt).one()
        session.delete(card)
        session.commit()


def get_all_cards(user_id):
    with Session(engine) as session:
        stmt = select(Card).where(Card.owner == user_id)
        cards = session.scalars(stmt).all()
    return cards


def add_card_to_db(front_side, back_side, user_id):
    with Session(engine) as session:
        card = Card(front_side=front_side, back_side=back_side, owner=user_id)
        session.add(card)
        session.commit()


def get_cards_to_check(user_id):
    pass
