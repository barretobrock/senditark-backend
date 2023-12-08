from typing import (
    Dict,
    List,
    Optional,
)

from sqlalchemy.orm import Session

from senditark_api.model import TablePayee
from senditark_api.utils.query.base import (
    BaseQueryHelper,
    FilterListType,
    ModelDictType,
)


class PayeeQueries(BaseQueryHelper):

    @classmethod
    def add_payee(cls, session: Session, data: ModelDictType) -> TablePayee:
        return cls._add_obj(session=session, obj_class=TablePayee, data=data)

    @classmethod
    def get_payee(cls, session: Session, payee_id: int) -> Optional[TablePayee]:
        return cls._get_obj(session=session, obj_class=TablePayee, filters=[TablePayee.payee_id == payee_id])

    @classmethod
    def get_payees(cls, session: Session, filters: FilterListType = None, limit: int = 100) -> List[TablePayee]:
        return cls._get_objs(session=session, obj_class=TablePayee, filters=filters, limit=limit)

    @classmethod
    def edit_payee(cls, session: Session, payee_id: int, data: ModelDictType):
        payee = cls.get_payee(session=session, payee_id=payee_id)
        if payee is None:
            raise ValueError(f'Failed to find payee with id: {payee_id}')
        cls._edit_obj(session=session, obj=payee, data=data)

    @classmethod
    def get_payee_data(cls, session: Session, payee_id: int = None, payee_obj: TablePayee = None) -> Dict:
        if payee_obj is None:
            payee_obj = cls.get_payee(session=session, payee_id=payee_id)

        return {
            'payee_id': payee_obj.payee_id,
            'payee_name': payee_obj.payee_name,
        }

    @classmethod
    def delete_payee(cls, session: Session, payee_id: int):
        """ Deletes the payee with the given id
        """
        cls.log.info(f'Handling DELETE for PAYEE ({payee_id})')

        payee = cls.get_payee(session=session, payee_id=payee_id)

        # Check for transactions that use payee
        if payee.transaction_splits:
            splits = payee.transaction_splits
            cls.log.debug(f'Found {len(splits)} transactions that link to this payee. '
                          f'Changing their references before deletion.')
            unnamed_payee = cls.get_or_create(session=session, obj=TablePayee(payee_name='UNNAMED'), attrs='payee_name')
            for split in splits:
                split.payee = unnamed_payee
                # NOTE: Not sure if needed, but saw some (latency?) issues when this was outside the loop
                #   in which the payee key was not properly updated for the last item in the loop.
                session.commit()
            cls.log.debug('Replacement completed. Proceeding with delete.')

        session.delete(payee)
        session.commit()


if __name__ == '__main__':
    from senditark_api.config import DevelopmentConfig

    DevelopmentConfig.build_db_engine()
    session = DevelopmentConfig.SESSION()
    pq = PayeeQueries
    pqdict = {
        TablePayee.payee_name.name: 'AnotherPaysdeemeter'
    }
    pq.add_payee(session=session, data=pqdict)
