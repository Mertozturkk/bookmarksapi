from flask_jwt_extended.view_decorators import jwt_required
from flask import Blueprint, request, jsonify
import validators
from src.constants.http_status_codes import *
from src.database import Bookmark,db
from flask_jwt_extended import get_jwt_identity
from flasgger import swag_from
bookmarks = Blueprint('bookmarks', __name__
                 , url_prefix='/api/v1/bookmarks')


@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    if request.method == 'POST':

        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({'error': 'Invalid URL'}), HTTP_400_BAD_REQUEST
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({'error': 'URL already exists'}), HTTP_409_CONFLICT

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }), HTTP_201_CREATED
    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page, per_page)

        data = []
        for bookmark in bookmarks.items:
            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'body': bookmark.body,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at
            })
        meta = {
            'page': bookmarks.page,
            'pages': bookmarks.pages,
            'total_count': bookmarks.total,
            'prev_page': bookmarks.prev_num,
            'next_page': bookmarks.next_num,
            'has_prev': bookmarks.has_prev,
            'has_next': bookmarks.has_next,
        }
        return jsonify({'data':data,
                        'meta':meta}), HTTP_200_OK


@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    return jsonify({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'body': bookmark.body,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at
            }), HTTP_200_OK

@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({'message': 'Item deleted'}), HTTP_200_OK


@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()

    if not bookmark:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({'error': 'Invalid URL'}), HTTP_400_BAD_REQUEST

    bookmark.body = body
    bookmark.url = url
    db.session.commit()
    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
    }), HTTP_200_OK


@bookmarks.get("/stats")
@jwt_required()
@swag_from('./docs/bookmarks/stats.yaml')
def get_stats():
    current_user = get_jwt_identity()
    data = []
    item = Bookmark.query.filter_by(user_id=current_user).all()
    for i in item:
        new_link = {
            'url': i.url,
            'short_url': i.short_url,
            'visits': i.visits,
            'id': i.id
        }
        data.append(new_link)
    return jsonify({'data': data}), HTTP_200_OK