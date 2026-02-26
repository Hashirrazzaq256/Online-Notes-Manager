import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'database.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        '''
    )

    # Notes table
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

    # Unique index on (user_id, client_id) to prevent duplicates on sync
    cursor.execute(
        '''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_notes_user_client
        ON notes(user_id, client_id)
        WHERE client_id IS NOT NULL;
        '''
    )

    conn.commit()
    conn.close()
    print("Initialized database at:", DB_PATH)


if __name__ == '__main__':
    init_db()
