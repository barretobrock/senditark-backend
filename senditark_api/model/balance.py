import datetime
from typing import Union

from sqlalchemy import (
    DATE,
    Column,
    Float,
    ForeignKey,
    Integer,
)

from .account import TableAccount
from .base import Base


class TableBalance(Base):
    """Balance table"""

    balance_id = Column(Integer, primary_key=True, autoincrement=True)
    account_key = Column(Integer, ForeignKey(TableAccount.account_id), nullable=False)
    date = Column(DATE, nullable=False)
    amount = Column(Float(2), nullable=False)

    def __init__(self, date: Union[str, date, datetime], amount: float, account_key: int = None):
        if not isinstance(date, datetime.date):
            if isinstance(date, str):
                date = datetime.datetime.strptime('%Y-%m-%d', date)
            elif isinstance(date, datetime.datetime):
                date = date.date
            else:
                raise ValueError(f'Unsupported type provided for balance.date: {type(date)}')
        if account_key is not None:
            self.account_key = account_key
        self.date = date
        self.amount = amount

    def __repr__(self) -> str:
        return f'<TableBalance(id={self.balance_id}, date={self.date:%F}, amount={self.amount})>'
