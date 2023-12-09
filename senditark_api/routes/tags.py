from flask import (
    Blueprint,
    jsonify,
    request,
)

from senditark_api.routes.helpers import get_session
from senditark_api.utils.query import SenditarkQueries as Query

bp_tag = Blueprint('tag', __name__, url_prefix='/tag')


@bp_tag.route('/all', methods=['GET'])
def get_all_tags():
    session = get_session()
    tags = Query.get_tags(session=session, limit=250)
    return jsonify(tags), 200


@bp_tag.route('/add', methods=['POST'])
def add_tag():
    session = get_session()
    data = request.get_json(force=True)

    new_tag = Query.add_tag(session=session, data=data)

    return jsonify({
        'success': True,
        'message': f'Tag {new_tag} successfully added!'
    }), 200


@bp_tag.route('/<int:tag_id>', methods=['GET'])
def get_tag(tag_id: int):
    session = get_session()
    tag = Query.get_tag(session=session, tag_id=tag_id)
    return jsonify(tag), 200


@bp_tag.route('/<int:tag_id>/edit', methods=['GET', 'POST'])
def edit_tag(tag_id: int):
    session = get_session()
    if request.method == 'GET':
        tag = Query.get_tag(session=session, tag_id=tag_id)
        return jsonify(tag), 200
    elif request.method == 'POST':
        tag = Query.edit_tag(session=session, tag_id=tag_id, data=request.get_json(force=True))
        return jsonify(tag), 200


@bp_tag.route('/<int:tag_id>/delete', methods=['DELETE'])
def delete_tag(tag_id: int):
    session = get_session()
    Query.delete_tag(session=session, tag_id=tag_id)
    return jsonify({
        'success': True,
        'message': f'Tag with id {tag_id} successfully deleted.'
    })
