import os
import sqlite3
import json
import uuid
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, g, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)

#  Application setup

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['DATABASE'] = os.path.join(app.root_path, 'database.db')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#  Database

def get_db():
    #  we arw opening a new database connection if none exists for this request.
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    # Initializing database tables if  don't exist
    db = get_db()
    cursor = db.cursor()

    # Users table (simple username + password hash)
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        '''
    )

    # Notes table for logged-in users
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            is_pinned INTEGER DEFAULT 0,
            reminder_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            client_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        '''
    )

    #  provdiding unique index for (user_id, client_id) to avoid duplicate imports
    cursor.execute(
        '''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_notes_user_client
        ON notes(user_id, client_id)
        WHERE client_id IS NOT NULL;
        '''
    )

    db.commit()


#  User model & authentication

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return User(id=row['id'], username=row['username'], password_hash=row['password_hash'])


def get_user_by_id(user_id):
    db = get_db()
    row = db.execute(
        'SELECT id, username, password_hash FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()
    return User.from_row(row)


def get_user_by_username(username):
    db = get_db()
    row = db.execute(
        'SELECT id, username, password_hash FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    return User.from_row(row)


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(int(user_id))


def create_user(username, password):
    # Creating a new user with a hashed password.
    db = get_db()
    password_hash = generate_password_hash(password)
    try:
        db.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, password_hash)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return None  # which means username already exists
    return get_user_by_username(username)


#  Notes helpers

def row_to_note_dict(row):
    # Here we are converting  a SQLite row to a plain dict for JSON/JS consumption.
    return {
        'id': row['id'],
        'title': row['title'],
        'content': row['content'],
        'category': row['category'] or '',
        'isPinned': bool(row['is_pinned']),
        'reminderAt': row['reminder_at'] or '',
        'createdAt': row['created_at'],
        'updatedAt': row['updated_at'],
        'clientId': row['client_id'] or ''
    }


def import_guest_notes_for_user(user_id, notes_json_string):
    # Herwe we are importing guest notes (localStorage)  into the database for this user.
    # notes_json_string is expected to be a JSOn

    if not notes_json_string:
        return

    try:
        notes = json.loads(notes_json_string)
    except json.JSONDecodeError:
        # If anything goes wrong, we simply skip importing to avoid crashing login.
        return

    if not isinstance(notes, list):
        return

    db = get_db()
    cursor = db.cursor()

    for n in notes:
        title = (n.get('title') or '').strip()
        content = (n.get('content') or '').strip()

        # Skip completely empty notes
        if not title and not content:
            continue

        category = (n.get('category') or '').strip()
        is_pinned = 1 if n.get('isPinned') else 0
        reminder_at = (n.get('reminderAt') or '').strip() or None
        client_id = (n.get('clientId') or '').strip() or None
        updated_at = (n.get('updatedAt') or datetime.utcnow().isoformat())
        created_at = n.get('createdAt') or updated_at

        try:
            cursor.execute(
                '''
                INSERT INTO notes
                    (user_id, title, content, category, is_pinned,
                     reminder_at, created_at, updated_at, client_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (user_id, title or 'Untitled', content, category, is_pinned,
                 reminder_at, created_at, updated_at, client_id)
            )
        except sqlite3.IntegrityError:
            # Probably duplicate (user_id, client_id); ignoring
            continue

    db.commit()


#  Routes

with app.app_context():
    init_db()


@app.route('/')
def index():
    # Main notes page (works for both guest and logged-in users).
    return render_template('dashboard.html', title='Dashboard')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # If already logged in, go straight to dashboard
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('register.html', title='Register')

        existing = get_user_by_username(username)
        if existing:
            flash('This username is already taken. Please choose another.', 'error')
            return render_template('register.html', title='Register')

        user = create_user(username, password)
        if user is None:
            flash('Could not create user. Please try again.', 'error')
            return render_template('register.html', title='Register')

        login_user(user)
        flash('Registration successful! You are now logged in.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        local_notes_json = request.form.get('local_notes', '')

        user = get_user_by_username(username)
        if user is None or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.', 'error')
            return render_template('login.html', title='Login')

        # Log the user in
        login_user(user)
        flash('Logged in successfully.', 'success')

        # Import guest notes into this user's account, if any.
        if local_notes_json:
            import_guest_notes_for_user(user.id, local_notes_json)

        return redirect(url_for('index'))

    return render_template('login.html', title='Login')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


#  Notes API (for authenticated users only)

@app.route('/api/notes', methods=['GET', 'POST'])
@login_required
def api_notes():
    db = get_db()
    if request.method == 'GET':
        rows = db.execute(
            '''
            SELECT id, title, content, category, is_pinned,
                   reminder_at, created_at, updated_at, client_id
            FROM notes
            WHERE user_id = ?
            ORDER BY is_pinned DESC, updated_at DESC
            ''',
            (current_user.id,)
        ).fetchall()
        notes = [row_to_note_dict(r) for r in rows]
        return jsonify(notes)

    # POST: create new note
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    category = (data.get('category') or '').strip()
    is_pinned = 1 if data.get('isPinned') else 0
    reminder_at = (data.get('reminderAt') or '').strip() or None
    client_id = (data.get('clientId') or '').strip() or str(uuid.uuid4())

    now_iso = datetime.utcnow().isoformat()
    if not title and not content:
        title = 'Untitled'

    cursor = db.cursor()
    cursor.execute(
        '''
        INSERT INTO notes
            (user_id, title, content, category, is_pinned,
             reminder_at, created_at, updated_at, client_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (current_user.id, title, content, category, is_pinned,
         reminder_at, now_iso, now_iso, client_id)
    )
    db.commit()

    note_id = cursor.lastrowid
    row = db.execute(
        '''
        SELECT id, title, content, category, is_pinned,
               reminder_at, created_at, updated_at, client_id
        FROM notes
        WHERE id = ? AND user_id = ?
        ''',
        (note_id, current_user.id)
    ).fetchone()
    return jsonify(row_to_note_dict(row)), 201


@app.route('/api/notes/<int:note_id>', methods=['PUT', 'DELETE'])
@login_required
def api_note_detail(note_id):
    db = get_db()
    # Verify the note belongs to the current user
    row = db.execute(
        '''
        SELECT id, title, content, category, is_pinned,
               reminder_at, created_at, updated_at, client_id
        FROM notes
        WHERE id = ? AND user_id = ?
        ''',
        (note_id, current_user.id)
    ).fetchone()

    if row is None:
        return jsonify({'error': 'Note not found'}), 404

    if request.method == 'DELETE':
        db.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, current_user.id))
        db.commit()
        return jsonify({'status': 'deleted'})

    # PUT: updating note
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or row['title']).strip()
    content = (data.get('content') or row['content']).strip()
    category = (data.get('category') or row['category'] or '').strip()
    if 'isPinned' in data:
        # If the key exists, use the new value (1 for true, 0 for false)
        is_pinned = 1 if data['isPinned'] else 0
    else:
        # If the key is missing, keep the old database value
        is_pinned = int(row['is_pinned'])
    reminder_at = (data.get('reminderAt') or row['reminder_at'] or '').strip() or None

    now_iso = datetime.utcnow().isoformat()
    db.execute(
        '''
        UPDATE notes
        SET title = ?, content = ?, category = ?, is_pinned = ?,
            reminder_at = ?, updated_at = ?
        WHERE id = ? AND user_id = ?
        ''',
        (title, content, category, is_pinned, reminder_at, now_iso, note_id, current_user.id)
    )
    db.commit()

    updated_row = db.execute(
        '''
        SELECT id, title, content, category, is_pinned,
               reminder_at, created_at, updated_at, client_id
        FROM notes
        WHERE id = ? AND user_id = ?
        ''',
        (note_id, current_user.id)
    ).fetchone()

    return jsonify(row_to_note_dict(updated_row))


if __name__ == '__main__':

    app.run(debug=True)
