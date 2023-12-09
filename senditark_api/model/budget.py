from dataclasses import dataclass
import datetime
import enum
from typing import List

from sqlalchemy import (
    VARCHAR,
    Column,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship

from .account import TableAccount
from .base import Base


class BudgetFrequency(enum.IntEnum):
    """Schedule frequencies - how often to run"""
    MONTHLY = enum.auto()
    QUARTERLY = enum.auto()
    ANNUALLY = enum.auto()


@dataclass
class TableBudget(Base):
    """Budget table"""

    budget_id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(VARCHAR, nullable=False)
    frequency: BudgetFrequency = Column(Enum(BudgetFrequency), default=BudgetFrequency.MONTHLY, nullable=False)
    budget_items = relationship('TableBudgetItem', back_populates='budget')
    start_date: datetime.date = Column(Date, nullable=False)

    def __init__(self, name: str, start_date: datetime.date, frequency: BudgetFrequency = BudgetFrequency.MONTHLY,
                 budget_items: List['TableBudgetItem'] = None):
        self.name = name
        self.start_date = start_date
        self.frequency = frequency
        if budget_items is not None:
            self.budget_items = budget_items

    def __repr__(self) -> str:
        return f'<TableBudget(name={self.name}, freq={self.frequency.name})>'


@dataclass
class TableBudgetItem(Base):
    """Budget Item table"""

    budget_item_id: int = Column(Integer, primary_key=True, autoincrement=True)
    budget_key: int = Column(Integer, ForeignKey(TableBudget.budget_id), nullable=False)
    budget = relationship('TableBudget', back_populates='budget_items')
    account_key: int = Column(Integer, ForeignKey(TableAccount.account_id), nullable=False)
    account = relationship('TableAccount', back_populates='budget_items')

    amount: float = Column(Float(2), nullable=False)
    year: int = Column(Integer, nullable=False)
    month: int = Column(Integer)
    quarter: int = Column(Integer)

    def __init__(self, amount: float, year: int, month: int = None, quarter: int = None,
                 budget: TableBudget = None, account: TableAccount = None):
        self.amount = amount
        self.year = year
        self.month = month
        self.quarter = quarter
        self.budget = budget
        self.account = account

    def __repr__(self) -> str:
        return f'<TableBudgetItem(amount={self.amount}, yyyy={self.year}, m={self.month}, q={self.quarter})>'
