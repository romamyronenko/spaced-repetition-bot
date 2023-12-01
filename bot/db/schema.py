from sqlalchemy import Column, Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Card(Base):
    __tablename__ = "card"

    id = Column(Integer, primary_key=True)
    front_side: Column[str] = Column(String(300))
    back_side = Column(String(300))
    owner: Column[int] = Column(Integer())

    def __repr__(self) -> str:
        return f"{self.front_side} - {self.back_side}"
