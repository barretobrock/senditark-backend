from dataclasses import dataclass
import datetime
import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DATE,
    VARCHAR,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    relationship,
)

from .account import TableAccount
from .base import Base
from .payee import TablePayee

if TYPE_CHECKING:
    from .tag import TableTagToScheduledTransactionSplit


class ScheduleFrequency(enum.IntEnum):
    """Schedule frequencies - how often to run"""
    WEEKLY = enum.auto()
    MONTHLY = enum.auto()
    QUARTERLY = enum.auto()
    ANNUALLY = enum.auto()


class ScheduleRule(enum.IntEnum):
    """Schedule rules - when to run"""
    NTH_DAY = enum.auto()   # Nth day of period (e.g., month)
    BEGIN = enum.auto()     # Beginning of period (e.g., month)
    END = enum.auto()       # End of period (e.g., month)
    DATE = enum.auto()      # Specific date (annual only)


@dataclass
class TableScheduledTransaction(Base):
    """Transactions table"""

    scheduled_transaction_id: int = Column(Integer, primary_key=True, autoincrement=True)
    frequency: ScheduleFrequency = Column(Enum(ScheduleFrequency), default=ScheduleFrequency.MONTHLY, nullable=False)
    rule: ScheduleRule = Column(Enum(ScheduleRule), default=ScheduleRule.END, nullable=False)
    split_templates: Mapped['TableScheduledTransactionSplit'] = relationship('TableScheduledTransactionSplit',
                                                                             back_populates='scheduled_transaction')
    start_date: datetime.date = Column(DATE, nullable=False)
    last_post_date: datetime.date = Column(DATE, nullable=True)
    next_post_date: datetime.date = Column(DATE, nullable=True)
    create_n_days_before: int = Column(Integer, default=30, nullable=False)
    description: str = Column(Text)

    def __init__(self, start_date: datetime.date, create_n_days_before: int = 30,
                 frequency: ScheduleFrequency = ScheduleFrequency.MONTHLY, rule: ScheduleRule = ScheduleRule.END,
                 description: str = None, split_templates: Mapped['TableScheduledTransactionSplit'] = None):
        if not isinstance(start_date, datetime.date):
            if isinstance(start_date, str):
                start_date = datetime.datetime.strptime('%Y-%m-%d', start_date)
            elif isinstance(start_date, datetime.datetime):
                start_date = start_date.date
            else:
                raise ValueError(f'Unsupported type provided for balance.date: {type(start_date)}')
        self.frequency = frequency
        self.rule = rule
        self.split_templates = split_templates
        self.start_date = start_date
        self.create_n_days_before = create_n_days_before
        self.description = description

    def __repr__(self) -> str:
        return f'<TableScheduledTransaction(start_date={self.start_date} n_before={self.create_n_days_before})>'


@dataclass
class TableScheduledTransactionSplit(Base):
    """Scheduled Transaction split table

    This stores a template of each split
    """

    scheduled_transaction_split_id: int = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_transaction_key: int = Column(Integer, ForeignKey(TableScheduledTransaction.scheduled_transaction_id),
                                            nullable=False)
    scheduled_transaction = relationship('TableScheduledTransaction', back_populates='split_templates')
    payee_key: int = Column(Integer, ForeignKey(TablePayee.payee_id), nullable=False)
    payee: Mapped['TablePayee'] = relationship('TablePayee', back_populates='scheduled_transaction_splits')
    credit_account_key: int = Column(Integer, ForeignKey(TableAccount.account_id), nullable=False)
    credit_account: Mapped[TableAccount] = relationship('TableAccount', backref='credit_scheduled_transaction_splits',
                                                        foreign_keys=[credit_account_key])
    debit_account_key: int = Column(Integer, ForeignKey(TableAccount.account_id), nullable=False)
    debit_account: Mapped[TableAccount] = relationship('TableAccount', backref='debit_scheduled_transaction_splits',
                                                       foreign_keys=[debit_account_key])
    amount: float = Column(Float, nullable=False)
    memo: str = Column(VARCHAR)
    tags: Mapped['TableTagToScheduledTransactionSplit'] = relationship('TableTagToScheduledTransactionSplit',
                                                                       back_populates='scheduled_transactions')

    def __init__(self, amount: float, payee: TablePayee, credit_account: TableAccount, debit_account: TableAccount,
                 memo: str = None, scheduled_transaction: TableScheduledTransaction = None,
                 tags: Mapped['TableTagToScheduledTransactionSplit'] = None):
        self.amount = amount
        self.credit_account = credit_account
        self.debit_account = debit_account
        self.payee = payee
        self.memo = memo
        self.scheduled_transaction = scheduled_transaction
        self.tags = tags

    def __repr__(self) -> str:
        return (f'<TableScheduledTransactionSplit(amount={self.amount} credit={self.credit_account}, '
                f'debit={self.debit_account})>')
