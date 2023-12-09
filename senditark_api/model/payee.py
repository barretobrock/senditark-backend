from dataclasses import dataclass

from sqlalchemy import (
    VARCHAR,
    Column,
    Integer,
)
from sqlalchemy.orm import relationship

from .base import Base


@dataclass
class TablePayee(Base):
    """Payee table"""

    payee_id: int = Column(Integer, primary_key=True, autoincrement=True)
    payee_name: str = Column(VARCHAR, nullable=False)
    transaction_splits = relationship('TableTransactionSplit', back_populates='payee')
    scheduled_transaction_splits = relationship('TableScheduledTransactionSplit', back_populates='payee')

    def __init__(self, payee_name: str):
        self.payee_name = payee_name

    def __repr__(self) -> str:
        return f'<TablePayee(id={self.payee_id}, name={self.payee_name})>'
