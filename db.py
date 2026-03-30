import sqlite3
import bcrypt

conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

def create_tables():
    # USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        password BLOB
    )
    """)

    # PORTFOLIO
    c.execute("""
    CREATE TABLE IF NOT EXISTS portfolio (
        coin TEXT,
        investment REAL,
        current REAL
    )
    """)

    # ALERTS (create if not exists)
    c.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        coin TEXT,
        target REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password BLOB)
""")

    # 🔥 FIX: ADD 'sent' COLUMN IF MISSING
    try:
        c.execute("ALTER TABLE alerts ADD COLUMN sent INTEGER DEFAULT 0")
    except:
        pass  # already exists

    # Default user
    import bcrypt
    c.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not c.fetchone():
        hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users VALUES (?, ?)", ("admin", hashed))

    conn.commit()

def add_user(username, password):
    import bcrypt

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        c.execute("INSERT INTO users VALUES (?,?)", (username, hashed))
        conn.commit()
        return True
    except:
        return False  # username already exists
    
def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    data = c.fetchone()
    if data:
        return bcrypt.checkpw(password.encode(), data[0])
    return False

def add_crypto(coin, investment, current):
    c.execute("INSERT INTO portfolio VALUES (?,?,?)", (coin, investment, current))
    conn.commit()

def get_data():
    c.execute("SELECT * FROM portfolio")
    return c.fetchall()

def delete_coin(coin):
    c.execute("DELETE FROM portfolio WHERE coin=?", (coin,))
    conn.commit()

def add_alert(coin, target):
    c.execute(
        "SELECT * FROM alerts WHERE coin=? AND target=?",
        (coin, target)
    )

    if not c.fetchone():
        c.execute(
            "INSERT INTO alerts (coin, target, sent) VALUES (?, ?, 0)",
            (coin, target)
        )
        conn.commit()

def get_alerts():
    c.execute("SELECT coin, target, sent FROM alerts")
    return c.fetchall()

def mark_alert_sent(coin, target):
    c.execute(
        "UPDATE alerts SET sent=1 WHERE coin=? AND target=?",
        (coin, target)
    )
    conn.commit()

def delete_alert(coin):
    c.execute("DELETE FROM alerts WHERE coin=?", (coin,))
    conn.commit()