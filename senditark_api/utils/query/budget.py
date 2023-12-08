from typing import (
    Dict,
    List,
)

from sqlalchemy.orm import Session

from senditark_api.model import TableBudget
from senditark_api.utils.query.base import (
    BaseQueryHelper,
    FilterListType,
    ModelDictType,
)


class BudgetQueries(BaseQueryHelper):

    @classmethod
    def add_budget(cls, session: Session, data: ModelDictType) -> TableBudget:
        return cls._add_obj(session=session, obj_class=TableBudget, data=data)

    @classmethod
    def get_budget(cls, session: Session, budget_id: int) -> TableBudget:
        return cls._get_obj(session=session, obj_class=TableBudget, filters=[TableBudget.budget_id == budget_id])

    @classmethod
    def get_budgets(cls, session: Session, filters: FilterListType = None, limit: int = 100) -> List[TableBudget]:
        return cls._get_objs(session=session, obj_class=TableBudget, filters=filters, limit=limit)

    @classmethod
    def edit_budget(cls, session: Session, budget_id: int, data: ModelDictType):
        budget_obj = cls.get_budget(session=session, budget_id=budget_id)
        if budget_obj is None:
            raise ValueError(f'Failed to find budget with id: {budget_id}')

        cls._edit_obj(session=session, obj=budget_obj, data=data)

    @classmethod
    def get_budget_data(cls, session: Session, budget_id: int = None, budget_obj: TableBudget = None) -> Dict:
        if budget_obj is None:
            budget_obj = cls.get_budget(session=session, budget_id=budget_id)

        return {
            'budget_id': budget_obj.budget_id,
            'budget_name': budget_obj.name,
            'account_key': budget_obj.account_key,
            'amount': budget_obj.amount,
            'year': budget_obj.year,
            'month': budget_obj.month,
            'start_date': budget_obj.start_date
        }

    @classmethod
    def delete_budget(cls, session: Session, budget_id: int):
        cls.log.info(f'Handling DELETE for BUDGET ({budget_id})')

        budget = cls.get_budget(session=session, budget_id=budget_id)

        session.delete(budget)
        session.commit()
