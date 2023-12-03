from sqlalchemy import (
    VARCHAR,
    Column,
    Integer,
)
from sqlalchemy.orm import relationship

from .base import Base


class TablePayee(Base):
    """Payee table"""

    payee_id = Column(Integer, primary_key=True, autoincrement=True)
    payee_name = Column(VARCHAR, nullable=False)
    transaction_splits = relationship('TableTransactionSplit', back_populates='payee')

    def __init__(self, name: str):
        self.payee_name = name

    def __repr__(self) -> str:
        return f'<TablePayee(id={self.payee_id}, name={self.payee_name})>'
