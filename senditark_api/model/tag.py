from sqlalchemy import (
    VARCHAR,
    Column,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship

from .base import Base
from .transaction import TableTransactionSplit


class TableTag(Base):
    """Tag table"""

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(VARCHAR, nullable=False, unique=True)
    tag_color = Column(VARCHAR, nullable=False, default='yellow')
    tag_maps = relationship('TableTagToTransactionSplit', back_populates='tag')

    def __init__(self, name: str, color: str = 'yellow'):
        self.tag_name = name
        self.tag_color = color

    def __repr__(self) -> str:
        return f'<TableTag(id={self.tag_id}, name={self.tag_name}, color={self.tag_color})>'


class TableTagToTransactionSplit(Base):
    """Tag-to-transaction-split table"""

    tag_to_transaction_split_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_split_key = Column(Integer, ForeignKey(TableTransactionSplit.transaction_split_id), nullable=False)
    tag_key = Column(Integer, ForeignKey(TableTag.tag_id), nullable=False)
    tag = relationship('TableTag', back_populates='tag_maps')
    transactions = relationship('TableTransactionSplit', back_populates='tags')
    scheduled_transactions = relationship('TableScheduledTransactionSplit', back_populates='tags')

    def __init__(self, tag: TableTag):
        self.tag = tag

    def __repr__(self) -> str:
        return f'<TableTagToTransactionSplit(id={self.tag_to_transaction_split_id})>'
