from collections import deque
import enum
from typing import List

from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Enum,
    Integer,
)
from sqlalchemy.ext.hybrid import hybrid_property
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
    """Accounts table"""

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    parent_account_key = Column(Integer, default=None, nullable=True)
    level = Column(Integer, default=0, nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    account_currency = Column(Enum(Currency), default=Currency.USD, nullable=False)
    transaction_splits = relationship('TableTransactionSplit', back_populates='account')
    scheduled_transaction_split_templates = relationship('TableScheduledTransactionSplit', back_populates='account')
    is_hidden = Column(Boolean, default=False, nullable=False)

    def __init__(self, name: str, account_type: AccountType,
                 account_currency: Currency, parent_account: 'TableAccount' = None,
                 is_hidden: bool = False):
        self.name = name.upper()
        self.parent_account = parent_account
        self.account_type = account_type
        self.account_currency = account_currency
        self.is_hidden = is_hidden
        if self.parent_account is not None:
            self.parent_account_key = self.parent_account.account_id
            self.level = len(self.get_parent_names())
        else:
            self.level = 0

    def get_parent_names(self) -> List[str]:
        parent_list = deque()
        parent: TableAccount
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

    @hybrid_property
    def full_name(self):
        if self.parent_account_key is not None:
            parents_str = '.'.join(self.get_parent_names())
            return f'{self.account_type.name}.{parents_str}.{self.name}'.upper()
        return f'{self.account_type.name}.{self.name}'.upper()

    def __repr__(self) -> str:
        return f'<TableAccount(name={self.name}, level({self.level}), is_hidden={self.is_hidden})>'
