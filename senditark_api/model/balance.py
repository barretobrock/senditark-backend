import datetime
from typing import Union

from sqlalchemy import (
    DATE,
    Column,
    Float,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship

from .account import TableAccount
from .base import Base


class TableBalance(Base):
    """Balance table

    Balances are as of the end of the date provided.

    This should be used to look up the starting figure for a transaction:
        e.g., Transaction for account 'I' of 2023-11-02, looks up for balance as of the most recent date before that.
    """

    balance_id = Column(Integer, primary_key=True, autoincrement=True)
    account_key = Column(Integer, ForeignKey(TableAccount.account_id), nullable=False)
    account = relationship('TableAccount', back_populates='daily_balances')
    date = Column(DATE, nullable=False)
    amount = Column(Float(2), nullable=False)

    def __init__(self, date: Union[str, date, datetime], amount: float, account: TableAccount = None):
        if not isinstance(date, datetime.date):
            if isinstance(date, str):
                date = datetime.datetime.strptime('%Y-%m-%d', date)
            elif isinstance(date, datetime.datetime):
                date = date.date
            else:
                raise ValueError(f'Unsupported type provided for balance.date: {type(date)}')
        self.account = account
        self.date = date
        self.amount = amount

    def __repr__(self) -> str:
        return f'<TableBalance(id={self.balance_id}, date={self.date:%F}, amount={self.amount})>'
