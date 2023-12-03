from collections import deque
import datetime
import enum
from typing import (
    List,
    Optional,
)

from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Date,
    Enum,
    Integer,
)
from sqlalchemy.orm import relationship

from .base import (
    Base,
    Currency,
)


class AccountType(enum.Enum):
    ASSET = enum.auto()
    EQUITY = enum.auto()
    EXPENSE = enum.auto()
    INCOME = enum.auto()
    LIABILITY = enum.auto()


class TableAccount(Base):
    """ParentAccount table"""
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    parent_account_key = Column(Integer)
    name = Column(VARCHAR, nullable=False)
    full_name = Column(VARCHAR, nullable=False, unique=True)
    desc = Column(VARCHAR)
    level = Column(Integer, default=0, nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    account_currency = Column(Enum(Currency), default=Currency.USD, nullable=False)
    last_reconciled = Column(Date)
    is_hidden = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    scheduled_transaction_split_templates = relationship('TableScheduledTransactionSplit', back_populates='account')
    daily_balances = relationship('TableBalance', back_populates='account')
    budgets = relationship('TableBudget', back_populates='account')

    def __init__(self, name: str, account_type: AccountType,
                 account_currency: Currency = Currency.USD, parent_account: 'TableAccount' = None,
                 is_hidden: bool = False, is_active: bool = True, desc: str = None,
                 last_reconciled: datetime.date = None):
        self.name = name.upper()
        self.desc = desc
        self.parent_account = parent_account
        self.account_type = account_type
        self.account_currency = account_currency
        self.last_reconciled = last_reconciled
        self.is_hidden = is_hidden
        self.is_active = is_active
        self.full_name = self.get_full_name()
        self.level = self.get_level()
        if self.parent_account is not None:
            if self.parent_account.account_id is None:
                raise AttributeError(f'Parent account for account "{self.name}" has not yet been committed.')
            self.parent_account_key = self.parent_account.account_id

    def get_parent_names(self) -> List[str]:
        parent_list = deque()
        parent: Optional[TableAccount]
        parent = self.parent_account
        while parent is not None:
            # So, we're going backwards up the hierarchy.
            # Therefore, every iteration is one more item 'before' the last.
            # deque.appendleft() operates in constant time, whereas something like insert(0, x) would have been linear
            parent_list.appendleft(parent.name)
            try:
                parent = parent.parent_account
            except AttributeError:
                parent = None
        return list(parent_list)

    def get_full_name(self):
        if self.parent_account is not None:
            parents_str = '.'.join(self.get_parent_names())
            return f'{self.account_type.name}.{parents_str}.{self.name}'.upper()
        return f'{self.account_type.name}.{self.name}'.upper()

    def get_level(self) -> int:
        if self.parent_account is not None:
            return len(self.get_parent_names())
        return 0

    def __repr__(self) -> str:
        return f'<TableAccount(name={self.name}, level({self.level}), is_hidden={self.is_hidden})>'
