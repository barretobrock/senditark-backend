from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    VARCHAR,
    Boolean,
    Column,
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


class TableInvoice(Base):
    """Invoices table"""

    invoice_id = Column(Integer, primary_key=True, autoincrement=True)
    splits = relationship('TableInvoiceSplit', back_populates='invoice', lazy='dynamic')
    created_date = Column(TIMESTAMP, nullable=False)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_date = Column(TIMESTAMP)
    is_paid = Column(Boolean, default=False, nullable=False)
    paid_date = Column(TIMESTAMP)
    notes = Column(Text)

    def __init__(self, created_date: datetime,
                 posted_date: datetime = None, is_paid: bool = False, pmt_date: datetime = None,
                 notes: str = None):
        self.created_date = created_date
        self.is_posted = posted_date is not None and posted_date.date() > datetime(2000, 1, 1).date()
        self.posted_date = posted_date
        self.is_paid = is_paid
        self.paid_date = pmt_date
        self.notes = notes

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

    invoice_split_id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_key = Column(Integer, ForeignKey(TableInvoice.invoice_id), nullable=False)
    invoice = relationship('TableInvoice', back_populates='splits')
    transaction_date = Column(TIMESTAMP, nullable=False)
    description = Column(VARCHAR, nullable=False)
    quantity = Column(Float(2), default=1.0, nullable=False)
    unit_price = Column(Float(2), nullable=False)
    discount = Column(Float(2), nullable=False)
    transaction_split = relationship('TableTransactionSplit', back_populates='invoice_split')

    @hybrid_property
    def total(self) -> float:
        return self.quantity * self.unit_price * (1 - self.discount)

    @total.expression
    def total(cls) -> float:
        return cls.quantity * cls.unit_price * (1 - cls.discount)

    def __init__(self, transaction_date: datetime, description: str, quantity: float, unit_price: float,
                 discount: float):
        self.transaction_date = transaction_date
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount = discount

    def __repr__(self) -> str:
        return f'<TableInvoiceSplit(date={self.transaction_date} desc={self.description[:20]} ' \
               f'amt={self.total} discount={self.discount:.2%})>'
