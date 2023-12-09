from dataclasses import dataclass
import datetime
from typing import List

from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import (
    func,
    select,
)

from .base import Base


@dataclass
class TableInvoice(Base):
    """Invoices table"""

    invoice_id: int = Column(Integer, primary_key=True, autoincrement=True)
    created_date: datetime.date = Column(Date, nullable=False)
    is_posted: bool = Column(Boolean, default=False, nullable=False)
    posted_date: datetime.date = Column(Date)
    is_paid: bool = Column(Boolean, default=False, nullable=False)
    paid_date: datetime.date = Column(Date)
    notes: str = Column(Text)
    splits = relationship('TableInvoiceSplit', back_populates='invoice')

    def __init__(self, created_date: datetime.date, posted_date: datetime.date = None, paid_date: datetime.date = None,
                 notes: str = None, splits: List['TableInvoiceSplit'] = None):
        self.created_date = created_date
        if posted_date is not None:
            self.is_posted = True
        self.posted_date = posted_date
        if paid_date is not None:
            self.is_paid = True
        self.paid_date = paid_date
        self.notes = notes
        if splits is not None:
            self.splits = splits

    @hybrid_property
    def total(self) -> float:
        if self.splits.count() == 0:
            return 0
        return sum([x.total for x in self.splits])

    @total.expression
    def total(cls):
        return (
            select([func.sum(TableInvoiceSplit.total)]).
            where(TableInvoiceSplit.invoice_key == cls.invoice_id).label('total')
        )

    def __repr__(self) -> str:
        return f'<TableInvoice(id={self.invoice_id} created={self.created_date} is_posted={self.is_posted} ' \
               f'is_paid={self.is_paid})>'


class TableInvoiceSplit(Base):
    """Splits in invoices"""

    invoice_split_id: int = Column(Integer, primary_key=True, autoincrement=True)
    invoice_key: int = Column(Integer, ForeignKey(TableInvoice.invoice_id), nullable=False)
    invoice = relationship('TableInvoice', back_populates='splits')
    transaction_date: datetime.date = Column(Date, nullable=False)
    description: str = Column(VARCHAR, nullable=False)
    quantity: float = Column(Float(2), default=1.0, nullable=False)
    unit_price: float = Column(Float(2), nullable=False)
    discount: float = Column(Float(2), nullable=False)
    transaction_split = relationship('TableTransactionSplit', back_populates='invoice_split')

    @hybrid_property
    def total(self) -> float:
        return self.quantity * self.unit_price * (1 - self.discount)

    @total.expression
    def total(cls) -> float:
        return cls.quantity * cls.unit_price * (1 - cls.discount)

    def __init__(self, transaction_date: datetime.date, description: str, quantity: float, unit_price: float,
                 discount: float):
        self.transaction_date = transaction_date
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount = discount

    def __repr__(self) -> str:
        return f'<TableInvoiceSplit(date={self.transaction_date} desc={self.description} ' \
               f'amt={self.total} discount={self.discount:.2%})>'
