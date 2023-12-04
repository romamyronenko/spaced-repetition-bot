import copy
import datetime

import pytest
from sqlalchemy import create_engine, select, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from db.schema import Card, Base
from db.dbmanager import DBManager

base = declarative_base()


class DBHelper:
    _memory_engine = create_engine("sqlite://")
    session = Session(_memory_engine)

    @pytest.fixture()
    def db_manager(self):
        Base.metadata.create_all(self._memory_engine)

        yield DBManager(self._memory_engine)

        Base.metadata.drop_all(bind=self._memory_engine)

    def add_card(self, card_data):
        card = Card(**card_data)

        self.session.add(card)
        self.session.commit()
        return card

    def is_card_in_table(self, card_data):
        stmt = select(Card).where(
            (Card.owner == card_data["owner"])
            & (Card.front_side == card_data["front_side"])
        )
        cards = self.session.scalars(stmt).all()
        return bool(cards)

    def assert_card_in_table(self, card_data):
        assert self.is_card_in_table(card_data)

    def assert_card_not_in_table(self, card_data):
        assert not self.is_card_in_table(card_data)


class TestDBManager(DBHelper):
    TEST_CARD_DATA = dict(
        front_side="front",
        back_side="back",
        owner=1,
        learn_date=datetime.date.today(),
        interval=3,
        id=1,
    )

    def test_add_card(self, db_manager):
        db_manager.add_card("front", "back", 1)

        self.assert_card_in_table(self.TEST_CARD_DATA)

    def test_remove_card(self, db_manager):
        self.add_card(self.TEST_CARD_DATA)

        db_manager.remove_card(
            owner=self.TEST_CARD_DATA["owner"],
            front_side=self.TEST_CARD_DATA["front_side"],
        )

        self.assert_card_not_in_table(self.TEST_CARD_DATA)

    def test_update_forget(self, db_manager):
        card = self.add_card(self.TEST_CARD_DATA)

        db_manager.update_forget(card_id=self.TEST_CARD_DATA["id"])

        assert card.interval == 1

    def test_update_remember(self, db_manager):
        card = self.add_card(self.TEST_CARD_DATA)

        db_manager.update_remember(card_id=self.TEST_CARD_DATA["id"])

        assert card.interval == 7

    def test_get_all_cards(self, db_manager):
        card_data = copy.copy(self.TEST_CARD_DATA)
        card_data.pop("id")
        for _ in range(5):
            self.add_card(card_data)

        cards = db_manager.get_all_cards(self.TEST_CARD_DATA["owner"])

        assert len(cards) == 5

    def test_get_cards_to_check(self, db_manager):
        card_data = copy.copy(self.TEST_CARD_DATA)
        card_data.pop("id")
        for delta in range(-3, 4, 1):
            card_data["learn_date"] = self.TEST_CARD_DATA[
                "learn_date"
            ] + datetime.timedelta(days=delta)
            self.add_card(card_data)

        cards = db_manager.get_cards_to_check(self.TEST_CARD_DATA["owner"])

        assert len(cards) == 4
