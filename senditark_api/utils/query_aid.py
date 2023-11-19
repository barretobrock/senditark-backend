from typing import (
    Dict,
    List,
    Tuple,
    Union,
)

from sqlalchemy.sql import (
    and_,
    asc,
)

from senditark_api.model import (
    AccountType,
    Currency,
    TableAccount,
    TableInvoice,
    TableInvoiceSplit,
    TableTransaction,
    TableTransactionSplit,
)

ACCOUNT_ATTRS = {
    'account_id',
    'name',
    'parent_account_key',
    'level',
    'account_type',
    'account_currency',
    'is_hidden',
    'full_name'
}
INVOICE_ATTRS = {}


class SenditarkQueries:

    TABLE_TO_ATTR_MAPPING = {
        'account': ACCOUNT_ATTRS,
        'invoice': INVOICE_ATTRS
    }

    @classmethod
    def _build_account_filters(
            cls,
            acct_name: Union[str, List[str]] = None,
            acct_full_name: Union[str, List[str]] = None,
            acct_type: Union[AccountType, List[AccountType]] = None,
            acct_currs: Union[Currency, List[Currency]] = None,
    ):
        attrs = {
            TableAccount.name: acct_name,
            TableAccount.full_name: acct_full_name,
            TableAccount.account_type: acct_type,
            TableAccount.account_currency: acct_currs
        }
        filters = []

        for tbl_attr, attr in attrs.items():
            if attr is not None:
                if isinstance(attr, list):
                    filt = tbl_attr.in_(attr)
                else:
                    filt = tbl_attr == attr
                filters.append(filt)
        return filters

    @classmethod
    def _clean_table_obj(cls, obj) -> Dict:
        data = {}
        if obj.__tablename__ not in cls.TABLE_TO_ATTR_MAPPING.keys():
            raise ValueError(f'Table object {obj.__tablename__} not in TABLE_TO_ATTR_MAPPING.')
        mpp = cls.TABLE_TO_ATTR_MAPPING[obj.__tablename__]
        for attr_name in mpp:
            obj_attr = getattr(obj, attr_name)
            if isinstance(obj_attr, (Currency, AccountType,)):
                obj_attr = obj_attr.name
            data[attr_name] = obj_attr
        return data

    @classmethod
    def _clean_table_objs(cls, objs) -> Union[Dict, List[Dict]]:
        processed_items = []
        if not isinstance(objs, list):
            return cls._clean_table_obj(obj=objs)
        for obj in objs:
            processed_items.append(cls._clean_table_obj(obj=obj))
        return processed_items

    # ----------------------------------
    # ACCOUNT
    # ----------------------------------
    @classmethod
    def get_accounts(cls, db_conn):
        accounts = db_conn.session.query(TableAccount).all()
        return cls._clean_table_objs(accounts)

    @classmethod
    def get_account_info(cls, db_conn, account_id: int) -> Tuple[Dict, List[Dict]]:
        account = db_conn.session.query(TableAccount).filter(
            TableAccount.account_id == account_id
        ).one_or_none()
        account = cls._clean_table_objs(account)

        transaction_splits = db_conn.session.query(TableTransactionSplit).join(
            TableAccount, TableTransactionSplit.account_key == account_id).join(
            TableTransaction, TableTransactionSplit.transaction_key == TableTransaction.transaction_id).order_by(
            asc(TableTransaction.transaction_date)).all()
        transaction_splits = cls._clean_table_objs(transaction_splits)
        return account, transaction_splits

    @classmethod
    def get_account_reconciliation_info(cls, db_conn, account_id: int):
        account = db_conn.session.query(TableAccount).filter(
            TableAccount.account_id == account_id
        ).one_or_none()

        transaction_splits = db_conn.session.query(TableTransactionSplit).join(
            TableAccount, TableTransactionSplit.account_key == account_id).join(
            TableTransaction, TableTransactionSplit.transaction_key == TableTransaction.transaction_id).order_by(
            asc(TableTransaction.transaction_date)).all()
        # TODO: process List[Dict]
        return {'account': account, 'splits': transaction_splits}

    # ----------------------------------
    # INVOICE
    # ----------------------------------
    @classmethod
    def get_invoice(cls, db_conn, invoice_id: int):
        invoice = db_conn.session.query(TableInvoice).filter(TableInvoice.invoice_id == invoice_id).one_or_none()
        # TODO: process
        return invoice

    @classmethod
    def get_invoices(cls, db_conn, limit: int = 100):
        invoices = db_conn.session.query(TableInvoice).limit(limit).all()
        # TODO: process
        return invoices

    @classmethod
    def get_invoice_splits(cls, db_conn, invoice_id: int):
        invoice_splits = db_conn.session.query(TableInvoice).\
            join(TableInvoiceSplit, TableInvoice.invoice_id == TableInvoiceSplit.invoice_key).\
            filter(and_(
                TableInvoice.invoice_id == invoice_id,
                TableInvoiceSplit.quantity != 0
            )).all()
        # TODO: process
        return invoice_splits
