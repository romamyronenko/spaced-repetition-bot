from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from db import engine
from db.dbmanager import DATE_FORMAT, MAX_INTERVAL
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
        card = Card(
            front_side=front_side,
            back_side=back_side,
            owner=user_id,
            learn_date=date.today().strftime("%Y-%m-%d"),
            interval=1,
        )
        session.add(card)
        session.commit()


def get_card_to_check(user_id):
    """
    next_interval
    next_date

    next_date += next_interval
    next_interval = next_interval * 2 + 1


    :param user_id:
    :return:
    """
    with Session(engine) as session:
        stmt = select(Card).where(
            (Card.owner == user_id)
            & (Card.learn_date <= date.today().strftime(DATE_FORMAT))
            & (Card.interval <= MAX_INTERVAL)
        )
        cards = session.scalars(stmt).all()
        card = cards[0] if cards else None
    return card


def update_remember(card_id):
    with Session(engine) as session:
        stmt = select(Card).where(Card.id == card_id)
        cards = session.scalars(stmt).all()
        for card in cards:
            card.learn_date = (
                datetime.strptime(str(card.learn_date), DATE_FORMAT)
                + timedelta(days=card.interval)
            ).strftime(DATE_FORMAT)
            card.interval = card.interval * 2 + 1
        session.flush()
        session.commit()


def update_forget(card_id):
    with Session(engine) as session:
        stmt = select(Card).where(Card.id == card_id)
        cards = session.scalars(stmt).all()
        for card in cards:
            card.learn_date = (date.today() + timedelta(days=card.interval)).strftime(
                DATE_FORMAT
            )
            card.interval = 1
        session.flush()
        session.commit()
