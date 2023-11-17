import enum

from sqlalchemy import (
    DATE,
    VARCHAR,
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .account import TableAccount
from .base import Base


class ScheduleFrequency(enum.Enum):
    """Schedule frequencies - how often to run"""
    WEEKLY = enum.auto()
    MONTHLY = enum.auto()
    QUARTERLY = enum.auto()
    ANNUALLY = enum.auto()


class ScheduleRule(enum.Enum):
    """Schedule rules - when to run"""
    NTH_DAY = enum.auto()   # Nth day of period (e.g., month)
    BEGIN = enum.auto()     # Beginning of period (e.g., month)
    END = enum.auto()       # End of period (e.g., month)
    DATE = enum.auto()      # Specific date (annual only)


class TableScheduledTransaction(Base):
    """Transactions table"""

    scheduled_transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    frequency = Column(Enum(ScheduleFrequency), default=ScheduleFrequency.MONTHLY, nullable=False)
    rule = Column(Enum(ScheduleRule), default=ScheduleRule.END, nullable=False)
    split_templates = relationship('TableScheduledTransactionSplit', back_populates='scheduled_transaction')
    start_date = Column(DATE, nullable=False)
    last_post_date = Column(DATE, nullable=True)
    next_post_date = Column(DATE, nullable=True)
    create_n_days_before = Column(Integer, default=30, nullable=False)
    desc = Column(Text)


class TableScheduledTransactionSplit(Base):
    """Scheduled Transaction split table

    This stores a template of each split
    """

    scheduled_transaction_split_id = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_transaction_key = Column(Integer, ForeignKey(TableScheduledTransaction.scheduled_transaction_id),
                                       nullable=False)
    scheduled_transaction = relationship('TableScheduledTransaction', back_populates='split_templates')
    account_key = Column(Integer, ForeignKey(TableAccount.account_id), nullable=False)
    account = relationship('TableAccount', back_populates='scheduled_transaction_split_templates')
    amount = Column(Float, nullable=False)
    is_credit = Column(Boolean)
    tag = Column(VARCHAR)
    memo = Column(VARCHAR)
