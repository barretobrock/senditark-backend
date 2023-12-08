
from senditark_api.utils.query.account import AccountQueries
from senditark_api.utils.query.invoice import InvoiceQueries
from senditark_api.utils.query.tag import TagQueries
from senditark_api.utils.query.transaction import TransactionQueries


class SenditarkQueries(
        AccountQueries,
        InvoiceQueries,
        TagQueries,
        TransactionQueries
):
    pass


if __name__ == '__main__':
    from senditark_api.config import DevelopmentConfig

    DevelopmentConfig.build_db_engine()
    session = DevelopmentConfig.SESSION()
    sq = SenditarkQueries
    sq.get_transactions_by_account(session=session, account_id=2)