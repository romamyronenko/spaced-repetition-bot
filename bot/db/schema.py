from sqlalchemy import Column, Integer, Date
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Card(Base):
    __tablename__ = "card"

    id: Column[int] = Column(Integer, primary_key=True)
    front_side: Column[str] = Column(String(300))
    back_side = Column(String(300))
    owner: Column[int] = Column(Integer())
    learn_date: Column[Date] = Column(Date())
    interval: Column[int] = Column(Integer())

    def __repr__(self) -> str:
        return f"{self.front_side} - {self.back_side}"
