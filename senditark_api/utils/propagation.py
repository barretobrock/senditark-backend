import datetime

from pukr import get_logger
from sqlalchemy.orm import Session

from senditark_api.model import (
    TableAccount,
    TableBalance,
    TableTransaction,
)
from senditark_api.utils.query import SenditarkQueries

log = get_logger()


class PropagationHelper:

    @classmethod
    def determine_account_balance_from_previous_balances(
            cls,
            session: Session,
            account: TableAccount,
            transaction_date: datetime.date,
            split_amount: float
    ) -> TableBalance:
        """Determines a given account balance from the most recently occurring previous balance"""
        # Get previous balances
        prevs = [bal for bal in account.daily_balances if bal.date < transaction_date]

        if len(prevs) == 0:
            log.debug('No previous balances found for account. Creating new balance entry.')
            bal_obj = TableBalance(date=transaction_date, amount=split_amount, account=account)
        else:
            log.debug('Iterating through past balances to find out most recent date before transaction.')
            prev_bal_obj = max(prevs, key=lambda obj: obj.date)
            log.debug(f'Adding balance entry from {prev_bal_obj} for transaction date ({transaction_date}).')
            bal_obj = TableBalance(date=transaction_date, amount=prev_bal_obj.amount + split_amount, account=account)
        session.add(bal_obj)
        session.commit()
        return bal_obj

    @classmethod
    def determine_account_balance_from_same_day_balance(
            cls,
            session: Session,
            account: TableAccount,
            same_day_bal: TableBalance,
            transaction_date: datetime.date
    ) -> TableBalance:
        """Determines the updated account balance for the given transaction day"""

        same_day_amount = SenditarkQueries.get_all_transaction_splits(
            session=session,
            acct=account,
            trans_date=transaction_date,
            as_sum=True
        )
        log.debug(f'Determined total amount for account for date {transaction_date} to be {same_day_amount}')

        # Determine current balance by retrieving previous date's balance
        prevs = [bal for bal in account.daily_balances if bal.date < transaction_date]
        if len(prevs) == 0:
            log.debug('No previous balances found for account. Applying pure sum of day\'s transactions.')
            same_day_bal.amount = same_day_amount
        else:
            log.debug('Iterating through past balances to find most recent date before transaction.')
            prev_bal = max(prevs, key=lambda obj: obj.date)
            log.debug(f'Accing balance entry from {prev_bal} for transaction date ({transaction_date}).')
            same_day_bal.amount = prev_bal.amount + same_day_amount
        session.commit()
        return same_day_bal

    @classmethod
    def adjust_split_balances(cls, session: Session, transaction: TableTransaction):
        trans_date = transaction.transaction_date
        for split in transaction.splits:
            # Iterate on debit & credit accounts
            for acct, split_type in zip([split.debit_account, split.credit_account], ['debit', 'credit']):
                log.debug(f'Working on account: {acct}, as {split_type}')
                # Check if there's an existing balance for the transaction date
                bal = next((x for x in acct.daily_balances if x.date == trans_date), None)
                split_amount = split.amount * 1 if split_type == 'debit' else split.amount * -1
                log.debug(f'Determined amount for split to be: {split_amount}')
                if bal is None:
                    log.debug(f'No balance entry found for transaction date: {trans_date}')
                    bal_obj = cls.determine_account_balance_from_previous_balances(
                        session=session,
                        account=acct,
                        transaction_date=trans_date,
                        split_amount=split_amount
                    )
                else:
                    log.debug('Existing balance entry found for given transaction date')
                    bal_obj = cls.determine_account_balance_from_same_day_balance(
                        session=session,
                        account=acct,
                        same_day_bal=bal,
                        transaction_date=trans_date
                    )
                log.debug('Beginning process to adjust balances ahead of transaction date...')
                # Adjust balances for any dates forward ;)
                following_bals = [bal for bal in acct.daily_balances if bal.date > trans_date]
                log.debug(f'Found {len(following_bals)} balance dates to adjust.')
                running_bal = bal_obj.amount
                for forward_bal in following_bals:
                    log.debug(f'Working on date {forward_bal.date}...')
                    same_day_amount = SenditarkQueries.get_all_transaction_splits(
                        session=session, acct=acct, trans_date=forward_bal.date, as_sum=True
                    )
                    running_bal += same_day_amount
                    forward_bal.amount = running_bal
                if len(following_bals) > 0:
                    log.debug('Committing balance changes.')
                    session.commit()
