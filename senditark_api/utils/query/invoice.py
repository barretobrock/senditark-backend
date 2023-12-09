from typing import (
    Dict,
    List,
    Optional,
)

from sqlalchemy.orm import Session
from sqlalchemy.sql import asc

from senditark_api.model import (
    TableInvoice,
    TableInvoiceSplit,
)
from senditark_api.utils.query.base import (
    BaseQueryHelper,
    FilterListType,
    ModelDictType,
)


class InvoiceQueries(BaseQueryHelper):

    @classmethod
    def add_invoice(cls, session: Session, obj: TableInvoice) -> TableInvoice:
        return cls._add_obj(session=session, obj_class=TableInvoice, obj=obj)

    @classmethod
    def get_invoice(cls, session: Session, invoice_id: int = None, filters: FilterListType = None) -> TableInvoice:
        if filters is None:
            filters = [TableInvoice.invoice_id == invoice_id]
        return cls._get_obj(session=session, obj_class=TableInvoice, filters=filters)

    @classmethod
    def get_invoices(cls, session: Session, limit: int = 100, filters: FilterListType = None) -> List[TableInvoice]:
        return cls._get_objs(session=session, obj_class=TableInvoice, filters=filters, limit=limit,
                             order_by=asc(TableInvoice.created_date))

    @classmethod
    def edit_invoice(cls, session: Session, invoice_id: int, data: ModelDictType):
        invoice = cls.get_invoice(session=session, invoice_id=invoice_id)
        if invoice is None:
            raise ValueError(f'Failed to find invoice with id: {invoice_id}')
        # TODO: Splits?
        cls._edit_obj(session=session, obj=invoice, data=data)

    @classmethod
    def delete_invoice(cls, session: Session, invoice_id: int):
        cls.log.info(f'Handling DELETE for INVOICE ({invoice_id})')

        invoice = cls.get_invoice(session=session, invoice_id=invoice_id)

        session.delete(invoice)
        session.commit()

    @classmethod
    def get_invoice_data(cls, session: Session, invoice_id: int, invoice_obj: TableInvoice = None) -> Dict:
        if invoice_obj is None:
            invoice_obj = cls.get_invoice(session=session, invoice_id=invoice_id)

        return {
            'invoice_id': invoice_obj.invoice_id,
            'created_date': invoice_obj.created_date,
            'is_posted': invoice_obj.is_posted,
            'posted_date': invoice_obj.posted_date,
            'is_paid': invoice_obj.is_paid,
            'paid_date': invoice_obj.paid_date,
            'notes': invoice_obj.notes,
        }

    @classmethod
    def get_invoice_split(cls, session: Session, invoice_split_id: int = None,
                          filters: FilterListType = None) -> Optional[TableInvoiceSplit]:
        if filters is None:
            filters = [TableInvoiceSplit.invoice_split_id == invoice_split_id]
        return cls._get_obj(session=session, obj_class=TableInvoiceSplit, filters=filters)

    @classmethod
    def get_invoice_splits(cls, session: Session, filters=FilterListType, limit: int = None) -> List[TableInvoiceSplit]:
        return cls._get_objs(session=session, obj_class=TableInvoiceSplit, filters=filters, limit=limit)

    @classmethod
    def edit_invoice_split(cls, session: Session, invoice_split_id: int, data: ModelDictType):
        invoice_split = cls.get_invoice_split(session=session, invoice_split_id=invoice_split_id)
        if invoice_split is None:
            raise ValueError(f'Failed to find invoice_split with id: {invoice_split_id}')
        cls._edit_obj(session=session, obj=invoice_split, data=data)

    @classmethod
    def delete_invoice_split(cls, session: Session, invoice_split_id: int):
        cls.log.info(f'Handling DELETE for INVOICE_SPLIT ({invoice_split_id})')

        invoice_split = cls.get_invoice_split(session=session, invoice_split_id=invoice_split_id)

        session.delete(invoice_split)
        session.commit()

    @classmethod
    def get_invoice_split_data(cls, session: Session, invoice_id: int = None, invoice_split_id: int = None,
                               invoice_split_obj: TableInvoiceSplit = None) -> Dict:
        if invoice_split_obj is None:
            if all(x is None for x in [invoice_id, invoice_split_id]):
                raise ValueError('Cannot look up invoice split without an id!')
            invoice_split_obj = cls.get_invoice_split(session=session, invoice_split_id=invoice_split_id)

        return {
            'invoice_split_id': invoice_split_obj.invoice_split_id,
            'invoice_id': invoice_split_obj.invoice_key,
            'transaction_date': invoice_split_obj.transaction_date,
            'description': invoice_split_obj.description,
            'quantity': invoice_split_obj.quantity,
            'unit_price': invoice_split_obj.unit_price,
            'discount': invoice_split_obj.discount,
        }
