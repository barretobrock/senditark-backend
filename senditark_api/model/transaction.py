from dataclasses import dataclass
import datetime
import enum
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
)

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
from sqlalchemy.orm import (
    Mapped,
    relationship,
)

from .account import TableAccount
from .base import Base
from .invoice import TableInvoiceSplit
from .payee import TablePayee

if TYPE_CHECKING:
    from .tag import TableTagToTransactionSplit


class ReconciledState(enum.Enum):
    """Reconciliation states"""
    n = 'NotReconciled'
    c = 'Cleared'
    y = 'Reconciled'


@dataclass
class TableTransaction(Base):
    """Transaction table"""
    transaction_id: int = Column(Integer, primary_key=True, autoincrement=True)
    transaction_date: datetime.date = Column(DATE, nullable=False)
    splits = relationship('TableTransactionSplit', back_populates='transaction')
    is_scheduled: bool = Column(Boolean, default=False)
    description: str = Column(Text)

    def __init__(self, transaction_date: datetime.date, description: str = None, is_scheduled: bool = False,
                 splits: List['TableTransactionSplit'] = None):
        if not isinstance(transaction_date, datetime.date):
            if isinstance(transaction_date, str):
                transaction_date = datetime.datetime.strptime('%Y-%m-%d', transaction_date)
            elif isinstance(transaction_date, datetime.datetime):
                transaction_date = transaction_date.date
            else:
                raise ValueError(f'Unsupported type provided for balance.date: {type(transaction_date)}')
        self.transaction_date = transaction_date
        self.description = description
        self.is_scheduled = is_scheduled
        if splits is not None:
            self.splits = splits

    def __repr__(self) -> str:
        return f'<TableTransaction(date={self.transaction_date} desc={self.description})>'


@dataclass
class TableTransactionSplit(Base):
    """Transaction Split table"""
    transaction_split_id: int = Column(Integer, primary_key=True, autoincrement=True)
    transaction_key: int = Column(Integer, ForeignKey(TableTransaction.transaction_id), nullable=False)
    transaction = relationship('TableTransaction', back_populates='splits')
    payee_key: int = Column(Integer, ForeignKey(TablePayee.payee_id), nullable=False)
    payee: Mapped['TablePayee'] = relationship('TablePayee', back_populates='transaction_splits')
    credit_account_key: int = Column(Integer, ForeignKey(TableAccount.account_id), nullable=False)
    credit_account: Mapped['TableAccount'] = relationship('TableAccount', backref='credit_transaction_splits',
                                                          foreign_keys=[credit_account_key])
    debit_account_key: int = Column(Integer, ForeignKey(TableAccount.account_id), nullable=False)
    debit_account: Mapped['TableAccount'] = relationship('TableAccount', backref='debit_transaction_splits',
                                                         foreign_keys=[debit_account_key])
    reconciled_state: ReconciledState = Column(Enum(ReconciledState), default=ReconciledState.n, nullable=False)
    invoice_split_key: int = Column(Integer, ForeignKey(TableInvoiceSplit.invoice_split_id), nullable=True)
    invoice_split = relationship('TableInvoiceSplit', back_populates='transaction_split')
    amount: float = Column(Float, nullable=False)
    memo: str = Column(VARCHAR)
    tags = relationship('TableTagToTransactionSplit', back_populates='transactions')

    def __init__(self, amount: float, payee: TablePayee, credit_account: TableAccount, debit_account: TableAccount,
                 memo: str = None, reconciled_state: ReconciledState = ReconciledState.n,
                 transaction: TableTransaction = None, tags: Optional[List['TableTagToTransactionSplit']] = None):
        self.amount = amount
        self.credit_account = credit_account
        self.debit_account = debit_account
        self.payee = payee
        self.memo = memo
        self.reconciled_state = reconciled_state
        self.transaction = transaction
        self.tags = tags

    def __repr__(self) -> str:
        return f'<TableTransactionSplit(amount={self.amount} credit={self.credit_account}, debit={self.debit_account})>'
