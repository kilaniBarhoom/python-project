from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import DatabaseManager
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'smart_records_secret_key_2024')

# Initialize database connection (will use MONGODB_URI from .env)
db = DatabaseManager()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')

        success, user_id, message = db.authenticate_user(username, password)

        if success:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
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

        success, message = db.create_user(username, password, fullname)

        if success:
            flash(message + ' Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
            return render_template('signup.html')

    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    username = session.get('username')
    records = db.read_all_records(user_id)

    return render_template('index.html', username=username, records=records)

@app.route('/add', methods=['GET', 'POST'])
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

        success, message = db.create_record(user_id, title, description, category)

        if success:
            flash(message, 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'error')
            return render_template('add.html')

    return render_template('add.html')

@app.route('/edit/<record_id>', methods=['GET', 'POST'])
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
            return redirect(url_for('edit_record', record_id=record_id))

        success, message = db.update_record(record_id, title, description, category, status)

        if success:
            flash(message, 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'error')
            return redirect(url_for('edit_record', record_id=record_id))

    # Get record details
    records = db.read_all_records(user_id)
    record = None
    for r in records:
        if r[0] == record_id:
            record = r
            break

    if not record:
        flash('Record not found!', 'error')
        return redirect(url_for('dashboard'))

    return render_template('edit.html', record=record)

@app.route('/delete/<record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    success, message = db.delete_record(record_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("✓ Flask application starting...")
    print("✓ Database initialized successfully!")
    print("✓ Server running at http://127.0.0.1:5000")
    app.run(debug=True)
