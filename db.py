"""
db.py — SQLite persistence layer for FitBot.

Single file database (fitbot.db) created automatically on first run.
No server, no install — sqlite3 is part of Python's standard library.

Schema (4 tables):
    users            -> one row per profile snapshot (age, weight, height, goal...)
    weight_logs      -> many rows per user, tracks weight over time
    chat_history      -> many rows per user, stores chatbot Q&A
    generated_plans   -> many rows per user, stores AI workout/meal plans

Relationships: users (1) -> (many) weight_logs / chat_history / generated_plans
via the user_id foreign key.
"""

import sqlite3
from datetime import datetime

DB_PATH = "fitbot.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates all tables if they don't already exist. Safe to call every run."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            goal TEXT NOT NULL,
            activity_level TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS weight_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weight REAL NOT NULL,
            logged_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS generated_plans (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    conn.commit()
    conn.close()


def create_user(age, gender, height, weight, goal, activity_level):
    """Inserts a new profile snapshot, returns the new user_id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (age, gender, height, weight, goal, activity_level, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (age, gender, height, weight, goal, activity_level, datetime.now().isoformat()))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def log_weight(user_id, weight):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO weight_logs (user_id, weight, logged_at)
        VALUES (?, ?, ?)
    """, (user_id, weight, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_weight_history(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT weight, logged_at FROM weight_logs
        WHERE user_id = ?
        ORDER BY logged_at ASC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def log_chat(user_id, role, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chat_history (user_id, role, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, role, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_chat_history(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT role, message FROM chat_history
        WHERE user_id = ?
        ORDER BY created_at ASC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def save_plan(user_id, plan_type, content):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO generated_plans (user_id, plan_type, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, plan_type, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_latest_plan(user_id, plan_type):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT content FROM generated_plans
        WHERE user_id = ? AND plan_type = ?
        ORDER BY created_at DESC LIMIT 1
    """, (user_id, plan_type))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
