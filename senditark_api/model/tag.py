from dataclasses import dataclass

from sqlalchemy import (
    VARCHAR,
    Column,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    relationship,
)

from .base import Base
from .scheduled_transaction import TableScheduledTransactionSplit
from .transaction import TableTransactionSplit


@dataclass
class TableTag(Base):
    """Tag table"""

    tag_id: int = Column(Integer, primary_key=True, autoincrement=True)
    tag_name: str = Column(VARCHAR, nullable=False, unique=True)
    tag_color: str = Column(VARCHAR, nullable=False, default='yellow')
    transaction_tag_maps = relationship('TableTagToTransactionSplit', back_populates='tag')
    scheduled_transaction_tag_maps = relationship('TableTagToScheduledTransactionSplit', back_populates='tag')

    def __init__(self, name: str, color: str = 'yellow'):
        self.tag_name = name
        self.tag_color = color

    def __repr__(self) -> str:
        return f'<TableTag(id={self.tag_id}, name={self.tag_name}, color={self.tag_color})>'


@dataclass
class TableTagToTransactionSplit(Base):
    """Tag-to-transaction-split table"""

    tag_to_transaction_split_id: int = Column(Integer, primary_key=True, autoincrement=True)
    transaction_split_key: int = Column(Integer, ForeignKey(TableTransactionSplit.transaction_split_id), nullable=False)
    tag_key: int = Column(Integer, ForeignKey(TableTag.tag_id), nullable=False)
    tag: Mapped[TableTag] = relationship('TableTag', back_populates='transaction_tag_maps')
    transactions = relationship('TableTransactionSplit', back_populates='tags')

    def __init__(self, tag: TableTag):
        self.tag = tag

    def __repr__(self) -> str:
        return f'<TableTagToTransactionSplit(id={self.tag_to_transaction_split_id})>'


@dataclass
class TableTagToScheduledTransactionSplit(Base):
    """Tag-to-scheduled-transaction-split table"""
    tag_to_scheduled_transaction_split_id: int
    transaction_split_key: int
    tag_key: int
    tag: Mapped[TableTag]

    tag_to_scheduled_transaction_split_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_split_key = Column(Integer, ForeignKey(TableScheduledTransactionSplit.scheduled_transaction_split_id),
                                   nullable=False)
    tag_key = Column(Integer, ForeignKey(TableTag.tag_id), nullable=False)
    tag = relationship('TableTag', back_populates='scheduled_transaction_tag_maps')
    scheduled_transactions = relationship('TableScheduledTransactionSplit', back_populates='tags')

    def __init__(self, tag: TableTag):
        self.tag = tag

    def __repr__(self) -> str:
        return f'<TableTagToScheduledTransactionSplit(id={self.tag_to_scheduled_transaction_split_id})>'
