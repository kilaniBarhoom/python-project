from flask import Blueprint, request, redirect, url_for, session, flash, jsonify
from models import CommentModel
from .auth_routes import login_required

comment_bp = Blueprint('comment', __name__)
comment_model = CommentModel()


@comment_bp.route('/add/<record_id>', methods=['POST'])
@login_required
def add_comment(record_id):
    """Add a comment to a record"""
    user_id = session.get('user_id')
    content = request.form.get('content', '')

    if not content:
        flash('Comment cannot be empty!', 'error')
        return redirect(url_for('record.view_record', record_id=record_id))

    success, message = comment_model.create_comment(record_id, user_id, content)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('record.view_record', record_id=record_id))


@comment_bp.route('/edit/<comment_id>', methods=['POST'])
@login_required
def edit_comment(comment_id):
    """Edit a comment"""
    user_id = session.get('user_id')
    content = request.form.get('content', '').strip()
    record_id = request.form.get('record_id')

    if not content:
        flash('Comment cannot be empty!', 'error')
        return redirect(url_for('record.view_record', record_id=record_id))

    success, message = comment_model.update_comment(comment_id, content, user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('record.view_record', record_id=record_id))


@comment_bp.route('/delete/<comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    user_id = session.get('user_id')
    record_id = request.form.get('record_id')

    success, message = comment_model.delete_comment(comment_id, user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('record.view_record', record_id=record_id))
