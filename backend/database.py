"""
Database module for Rekuu AI Chatbot
"""

import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rekuu.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT DEFAULT 'New Chat',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        message_type TEXT DEFAULT 'text',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)''')
    conn.commit()
    conn.close()

def create_user(name, email, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (name, email, password_hash))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT id, name, email, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def create_chat_session(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat_sessions (user_id) VALUES (?)', (user_id,))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

def get_chat_sessions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    sessions = cursor.execute('SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.close()
    return sessions

def get_chat_session(session_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    session = cursor.execute('SELECT * FROM chat_sessions WHERE id = ? AND user_id = ?', (session_id, user_id)).fetchone()
    conn.close()
    return session

def delete_chat_session(session_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_sessions WHERE id = ? AND user_id = ?', (session_id, user_id))
    conn.commit()
    conn.close()

def save_message(session_id, user_id, role, content, message_type='text'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (session_id, user_id, role, content, message_type) VALUES (?, ?, ?, ?, ?)', (session_id, user_id, role, content, message_type))
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id

def get_chat_history(session_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    messages = cursor.execute('SELECT * FROM messages WHERE session_id = ? AND user_id = ? ORDER BY created_at ASC', (session_id, user_id)).fetchall()
    conn.close()
    return messages

def get_all_user_chats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    sessions = cursor.execute('''SELECT cs.*, (SELECT content FROM messages WHERE session_id = cs.id ORDER BY created_at DESC LIMIT 1) as last_message FROM chat_sessions cs WHERE cs.user_id = ? ORDER BY cs.created_at DESC''', (user_id,)).fetchall()
    conn.close()
    return sessions

def update_chat_title(session_id, user_id, title):
    """Update the title of a chat session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE chat_sessions SET title = ? WHERE id = ? AND user_id = ?', (title, session_id, user_id))
    conn.commit()
    conn.close()

def get_first_message(session_id, user_id):
    """Get the first user message from a chat session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    message = cursor.execute('SELECT content FROM messages WHERE session_id = ? AND user_id = ? AND role = ? ORDER BY created_at ASC LIMIT 1', (session_id, user_id, 'user')).fetchone()
    conn.close()
    return message['content'] if message else None

