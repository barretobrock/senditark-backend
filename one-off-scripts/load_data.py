from pukr import get_logger
from sqlalchemy.orm import Session

from senditark_api.config import DevelopmentConfig
from senditark_api.model import (
    AccountType,
    Currency,
    TableAccount,
    TableBalance,
    TableBudget,
    TableInvoice,
    TableInvoiceSplit,
    TableScheduledTransaction,
    TableScheduledTransactionSplit,
    TableTransaction,
    TableTransactionSplit,
)

log = get_logger()

TABLES = [
    TableAccount,
    TableBalance,
    TableBudget,
    TableInvoice,
    TableInvoiceSplit,
    TableScheduledTransaction,
    TableScheduledTransactionSplit,
    TableTransaction,
    TableTransactionSplit
]


def load_data(session: Session):
    acct1 = TableAccount(
        name='MY_CHK',
        account_type=AccountType.ASSET,
        account_currency=Currency.USD
    )
    acct2 = TableAccount(
        name='MY_CC',
        account_type=AccountType.LIABILITY,
        account_currency=Currency.USD
    )
    session.add_all([acct1, acct2])
    session.commit()


if __name__ == '__main__':
    DevelopmentConfig.build_db_engine()
    session = DevelopmentConfig.SESSION()
    load_data(session)
