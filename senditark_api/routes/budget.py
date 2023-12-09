from flask import (
    Blueprint,
    jsonify,
    request,
)

from senditark_api.routes.helpers import get_session
from senditark_api.utils.query import SenditarkQueries as Query

bp_budg = Blueprint('budget', __name__, url_prefix='/budget')


@bp_budg.route('/all', methods=['GET'])
def get_all_budgets():
    session = get_session()
    budgets = Query.get_budgets(session=session, limit=250)
    return jsonify(budgets), 200


@bp_budg.route('/add',  methods=['POST'])
def add_budget():
    # session = get_session()
    # data = request.get_json(force=True)

    # TODO: parse items if variable. If constant, take frequency and add items for each increment
    pass


@bp_budg.route('/<int:budget_id>',  methods=['GET'])
def get_budget(budget_id: int):
    session = get_session()
    budget = Query.get_budget(session=session, budget_id=budget_id)
    return jsonify(budget), 200


@bp_budg.route('/<int:budget_id>/edit',  methods=['GET', 'POST'])
def edit_budget(budget_id: int):
    session = get_session()
    if request.method == 'GET':
        budget = Query.get_budget(session=session, budget_id=budget_id)
        return jsonify(budget), 200
    elif request.method == 'POST':
        budget = Query.edit_budget(session=session, budget_id=budget_id, data=request.get_json(force=True))
        return jsonify(budget), 200


@bp_budg.route('/<int:budget_id>/delete', methods=['DELETE'])
def delete_budget(budget_id: int):
    session = get_session()
    Query.delete_budget(session=session, budget_id=budget_id)
    return jsonify({
        'success': True,
        'message': f'Budget with id {budget_id} successfully deleted.'
    })
