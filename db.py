"""
db.py
SQLite database layer for AI Fitness Coach
"""

import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "fitbot_v2.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(

        user_id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        age INTEGER,

        gender TEXT,

        height REAL,

        weight REAL,

        goal TEXT,

        activity_level TEXT,

        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS weight_logs(

        log_id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        weight REAL,

        logged_at TEXT,

        FOREIGN KEY(user_id)
        REFERENCES users(user_id)

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history(

        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        role TEXT,

        message TEXT,

        created_at TEXT,

        FOREIGN KEY(user_id)
        REFERENCES users(user_id)

    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS generated_plans(

        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        plan_type TEXT,

        content TEXT,

        created_at TEXT,

        FOREIGN KEY(user_id)
        REFERENCES users(user_id)

    )
    """)

    conn.commit()
    conn.close()


####################################################
# USER
####################################################

def register_user(
        name,
        email,
        password,
        age,
        gender,
        height,
        weight,
        goal,
        activity):

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT user_id FROM users WHERE email=?",
            (email,)
        )
    except Exception as e:
        print(e)
        raise

    if cur.fetchone():

        conn.close()

        return None

    password = hash_password(password)

    cur.execute("""

    INSERT INTO users(

        name,
        email,
        password,
        age,
        gender,
        height,
        weight,
        goal,
        activity_level,
        created_at

    )

    VALUES(?,?,?,?,?,?,?,?,?,?)

    """,

    (

        name,
        email,
        password,
        age,
        gender,
        height,
        weight,
        goal,
        activity,
        datetime.now().isoformat()

    ))

    conn.commit()

    user_id = cur.lastrowid

    conn.close()

    return user_id


def login_user(email,password):

    conn = get_connection()

    cur = conn.cursor()

    password = hash_password(password)

    cur.execute("""

    SELECT user_id

    FROM users

    WHERE email=?
    AND password=?

    """,

    (

        email,
        password

    ))

    row = cur.fetchone()

    conn.close()

    if row:

        return row[0]

    return None


def get_user(user_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""

    SELECT *

    FROM users

    WHERE user_id=?

    """,(user_id,))

    row = cur.fetchone()

    conn.close()

    return row

####################################################
# WEIGHT LOGS
####################################################

def log_weight(user_id, weight):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO weight_logs(
            user_id,
            weight,
            logged_at
        )
        VALUES(?,?,?)
        """,
        (
            user_id,
            weight,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_weight_history(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT weight, logged_at
        FROM weight_logs
        WHERE user_id=?
        ORDER BY logged_at ASC
        """,
        (user_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows


####################################################
# CHAT HISTORY
####################################################

def log_chat(user_id, role, message):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO chat_history(
            user_id,
            role,
            message,
            created_at
        )
        VALUES(?,?,?,?)
        """,
        (
            user_id,
            role,
            message,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_chat_history(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, message
        FROM chat_history
        WHERE user_id=?
        ORDER BY created_at ASC
        """,
        (user_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows


####################################################
# AI PLANS
####################################################

def save_plan(user_id, plan_type, content):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO generated_plans(
            user_id,
            plan_type,
            content,
            created_at
        )
        VALUES(?,?,?,?)
        """,
        (
            user_id,
            plan_type,
            content,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_latest_plan(user_id, plan_type):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT content
        FROM generated_plans
        WHERE user_id=?
        AND plan_type=?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (
            user_id,
            plan_type
        )
    )

    row = cur.fetchone()

    conn.close()

    return row[0] if row else None


def get_all_workouts(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT content, created_at
        FROM generated_plans
        WHERE user_id=?
        AND plan_type='workout'
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows


def get_all_meals(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT content, created_at
        FROM generated_plans
        WHERE user_id=?
        AND plan_type='meal'
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows


####################################################
# UPDATE PROFILE
####################################################

def update_profile(
    user_id,
    age,
    gender,
    height,
    weight,
    goal,
    activity
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET
            age=?,
            gender=?,
            height=?,
            weight=?,
            goal=?,
            activity_level=?
        WHERE user_id=?
        """,
        (
            age,
            gender,
            height,
            weight,
            goal,
            activity,
            user_id
        )
    )

    conn.commit()
    conn.close()
