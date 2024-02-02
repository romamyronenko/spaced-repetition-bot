from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.schema import Card

DATE_FORMAT = "%Y-%m-%d"
MAX_INTERVAL = 31


# TODO: add type annotations


class DBManager:
    def __init__(self, engine):
        self._engine = engine
        self._session = Session(self._engine)

    def add_card(self, front_side, back_side, user_id):
        card = Card(
            front_side=front_side,
            back_side=back_side,
            owner=user_id,
            learn_date=date.today(),
            interval=1,
        )
        self._session.add(card)
        self._session.commit()

    def remove_card(self, owner, front_side):
        stmt = select(Card).where(
            (Card.front_side == front_side) & (Card.owner == owner)
        )
        card = self._session.scalars(stmt).one()
        self._session.delete(card)
        self._session.commit()

    def update_forget(self, card_id):
        stmt = select(Card).where(Card.id == card_id)
        cards = self._session.scalars(stmt).all()
        for card in cards:
            card.learn_date = date.today() + timedelta(days=card.interval)
            card.interval = 1
        self._session.flush()
        self._session.commit()

    def update_remember(self, card_id):
        stmt = select(Card).where(Card.id == card_id)
        cards = self._session.scalars(stmt).all()
        for card in cards:
            card.learn_date = date.today() + timedelta(days=card.interval)
            card.interval = card.interval * 2 + 1
        self._session.flush()
        self._session.commit()

    def get_all_cards(self, user_id):
        stmt = select(Card).where(Card.owner == user_id)
        cards = self._session.scalars(stmt).all()
        return cards

    def get_cards_to_check(self, user_id):
        stmt = select(Card).where(
            (Card.owner == user_id)
            & (Card.learn_date <= date.today().strftime(DATE_FORMAT))
            & (Card.interval <= MAX_INTERVAL)
        )
        cards = self._session.scalars(stmt).all()
        return cards

    def get_card_to_check(self, user_id):
        cards = self.get_cards_to_check(user_id)
        return cards[0] if cards else None
