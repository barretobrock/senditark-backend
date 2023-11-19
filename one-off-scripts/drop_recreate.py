from pukr import get_logger
from sqlalchemy import (
    Engine,
    create_engine,
)

from senditark_api.config import DevelopmentConfig
from senditark_api.model import (
    Base,
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


def drop_and_recreate(eng: Engine):
    log.info('Dropping all tables...')
    tbl_objs = []
    for table in TABLES:
        # Try to get table from db. Returns None if not exist
        tbl_obj = Base.metadata.tables.get(table.__tablename__)
        if tbl_obj is None:
            log.info(f'Bypassing table {table.__tablename__}. Does not exist in db.')
            continue
        tbl_objs.append(Base.metadata.tables.get(table.__tablename__))
    if len(tbl_objs) > 0:
        log.info(f'Dropping {len(tbl_objs)} tables...')
        Base.metadata.drop_all(eng, tables=tbl_objs)
    else:
        log.info('Bypassed drop. No existing tables to drop')
    log.info('Recreating all tables...')
    Base.metadata.create_all(eng)


if __name__ == '__main__':
    DevelopmentConfig.build_db_engine()
    engine = create_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI, isolation_level='SERIALIZABLE')
    drop_and_recreate(engine)
