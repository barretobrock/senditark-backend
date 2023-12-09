from flask import (
    Blueprint,
    jsonify,
    request,
)

from senditark_api.routes.helpers import get_session
from senditark_api.utils.query import SenditarkQueries as Query

bp_payee = Blueprint('payee', __name__, url_prefix='/payee')


@bp_payee.route('/all', methods=['GET'])
def get_all_payees():
    session = get_session()
    payees = Query.get_payees(session=session, limit=250)
    return jsonify(payees), 200


@bp_payee.route('/add', methods=['POST'])
def add_payee():
    session = get_session()
    data = request.get_json(force=True)

    new_payee = Query.add_payee(session=session, data=data)

    return jsonify({
        'success': True,
        'message': f'Payee {new_payee} successfully added!'
    }), 200


@bp_payee.route('/<int:payee_id>', methods=['GET'])
def get_payee(payee_id: int):
    session = get_session()
    payee = Query.get_payee(session=session, payee_id=payee_id)
    return jsonify(payee), 200


@bp_payee.route('/<int:payee_id>/edit', methods=['GET', 'POST'])
def edit_payee(payee_id: int):
    session = get_session()
    if request.method == 'GET':
        payee = Query.get_payee(session=session, payee_id=payee_id)
        return jsonify(payee), 200
    elif request.method == 'POST':
        payee = Query.edit_payee(session=session, payee_id=payee_id, data=request.get_json(force=True))
        return jsonify(payee), 200


@bp_payee.route('/<int:payee_id>/delete', methods=['DELETE'])
def delete_payee(payee_id: int):
    session = get_session()
    Query.delete_payee(session=session, payee_id=payee_id)
    return jsonify({
        'success': True,
        'message': f'Payee with id {payee_id} successfully deleted.'
    })
