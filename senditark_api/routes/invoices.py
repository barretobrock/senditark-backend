from flask import (
    Blueprint,
    jsonify,
)

from senditark_api.routes.helpers import get_db_conn
from senditark_api.utils.query_aid import SenditarkQueries

bp_invc = Blueprint('invoice', __name__, url_prefix='/invoice')


@bp_invc.route('/all')
def get_all_invoices():
    invoices = SenditarkQueries.get_invoices(get_db_conn())
    return jsonify(invoices)


@bp_invc.route('/<int:invoice_id>')
def get_invoice(invoice_id: int):
    invoice = SenditarkQueries.get_invoice(get_db_conn(), invoice_id=invoice_id)
    invoice_splits = SenditarkQueries.get_invoice_splits(get_db_conn(), invoice_id=invoice_id)
    return jsonify({
        'invoice': invoice,
        'invoice-splits': invoice_splits
    })
