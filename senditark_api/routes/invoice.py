from flask import (
    Blueprint,
    jsonify,
    request,
)

from senditark_api.routes.helpers import get_session
from senditark_api.utils.query import SenditarkQueries as Query

bp_invc = Blueprint('invoice', __name__, url_prefix='/invoice')


@bp_invc.route('/all', methods=['GET'])
def get_all_invoices():
    session = get_session()
    invoices = Query.get_invoices(session=session, limit=250)
    return jsonify(invoices), 200


@bp_invc.route('/add', methods=['POST'])
def add_invoice():
    # session = get_session()
    # data = request.get_json(force=True)
    # TODO: Manually build out invoice and split object
    pass


@bp_invc.route('/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id: int):
    session = get_session()
    invoice = Query.get_invoice(session=session, invoice_id=invoice_id)
    return jsonify(invoice), 200


@bp_invc.route('/<int:invoice_id>/edit', methods=['GET', 'POST'])
def edit_invoice(invoice_id: int):
    session = get_session()
    if request.method == 'GET':
        invoice = Query.get_invoice(session=session, invoice_id=invoice_id)
        return jsonify(invoice), 200
    elif request.method == 'POST':
        invoice = Query.edit_invoice(session=session, invoice_id=invoice_id, data=request.get_json(force=True))
        return jsonify(invoice), 200


@bp_invc.route('/<int:invoice_id>/delete', methods=['DELETE'])
def delete_invoice(invoice_id: int):
    session = get_session()
    Query.delete_invoice(session=session, invoice_id=invoice_id)
    return jsonify({
        'success': True,
        'message': f'Invoice with id {invoice_id} successfully deleted.'
    })
