import sqlite3
import json
from datetime import datetime

DB_PATH = "claude_conversations.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            messages TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_conversation(conversation_id, messages):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    title = next((m["content"][:40] + "..." if len(m["content"]) > 40 
                  else m["content"] for m in messages 
                  if m["role"] == "user"), "New Chat")
    
    if conversation_id is None:
        cursor.execute("""
            INSERT INTO conversations (title, messages, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (title, json.dumps(messages), datetime.now(), datetime.now()))
        conversation_id = cursor.lastrowid
    else:
        cursor.execute("""
            UPDATE conversations 
            SET messages = ?, title = ?, updated_at = ?
            WHERE id = ?
        """, (json.dumps(messages), title, datetime.now(), conversation_id))
    
    conn.commit()
    conn.close()
    return conversation_id

def load_all_conversations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, updated_at 
        FROM conversations 
        ORDER BY updated_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def load_conversation(conversation_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT messages FROM conversations WHERE id = ?", (conversation_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []

def delete_conversation(conversation_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()