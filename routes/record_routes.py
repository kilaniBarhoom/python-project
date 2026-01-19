"""
Record routes for CRUD operations
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import RecordModel, CommentModel
from .auth_routes import login_required

record_bp = Blueprint('record', __name__)
record_model = RecordModel()
comment_model = CommentModel()


@record_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    username = session.get('username')
    records = record_model.read_all_records(user_id)

    return render_template('index.html', username=username, records=records)


@record_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_record():
    if request.method == 'POST':
        user_id = session.get('user_id')
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'General')

        if not title:
            flash('Title is required!', 'error')
            return render_template('add.html')

        if not description:
            flash('Description is required!', 'error')
            return render_template('add.html')

        success, message = record_model.create_record(user_id, title, description, category)

        if success:
            flash(message, 'success')
            return redirect(url_for('record.dashboard'))
        else:
            flash(message, 'error')
            return render_template('add.html')

    return render_template('add.html')


@record_bp.route('/edit/<record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    user_id = session.get('user_id')

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'General')
        status = request.form.get('status', 'Active')

        if not title or not description:
            flash('All fields are required!', 'error')
            return redirect(url_for('record.edit_record', record_id=record_id))

        success, message = record_model.update_record(record_id, title, description, category, status)

        if success:
            flash(message, 'success')
            return redirect(url_for('record.dashboard'))
        else:
            flash(message, 'error')
            return redirect(url_for('record.edit_record', record_id=record_id))

    # Get record details
    records = record_model.read_all_records(user_id)
    record = None
    for r in records:
        if r[0] == record_id:
            record = r
            break

    if not record:
        flash('Record not found!', 'error')
        return redirect(url_for('record.dashboard'))

    return render_template('edit.html', record=record)


@record_bp.route('/delete/<record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    success, message = record_model.delete_record(record_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('record.dashboard'))


@record_bp.route('/view/<record_id>')
@login_required
def view_record(record_id):
    """View a single record with its comments"""
    user_id = session.get('user_id')
    username = session.get('username')

    # Get record details
    record_doc = record_model.get_record_by_id(record_id)

    if not record_doc:
        flash('Record not found!', 'error')
        return redirect(url_for('record.dashboard'))

    # Check if record belongs to user
    if record_doc['user_id'] != user_id:
        flash('You do not have permission to view this record!', 'error')
        return redirect(url_for('record.dashboard'))

    # Format record
    record = (
        str(record_doc['_id']),
        record_doc['title'],
        record_doc['description'],
        record_doc['category'],
        record_doc['date_added'].strftime('%Y-%m-%d %H:%M:%S'),
        record_doc['status']
    )

    # Get comments for this record
    comments = comment_model.get_comments_by_record(record_id)
    comment_count = len(comments)

    return render_template('view_record.html', record=record, comments=comments,
                         comment_count=comment_count, username=username)
