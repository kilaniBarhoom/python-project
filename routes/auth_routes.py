"""
Authentication routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import UserModel

auth_bp = Blueprint('auth', __name__)
user_model = UserModel()


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('record.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')

        success, user_id, message = user_model.authenticate_user(username, password)

        if success:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('record.dashboard'))
        else:
            flash(message, 'error')
            return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not all([fullname, username, password, confirm_password]):
            flash('All fields are required!', 'error')
            return render_template('signup.html')

        if len(username) < 4:
            flash('Username must be at least 4 characters', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('signup.html')

        success, message = user_model.create_user(username, password, fullname)

        if success:
            flash(message + ' Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
            return render_template('signup.html')

    return render_template('signup.html')


@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
