import sqlite3
import datetime
import random

DB_PATH = "stats.db"

INITIAL_PRIZES = [
    ("Gemini Pro 18 Ay", 2),
    ("Microsoft 365 Plus 1 İl", 1),
    ("Canva Pro 2 İl", 2)
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            first_seen TEXT,
            last_seen TEXT,
            search_count INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            timestamp TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wheel_prizes (
            name TEXT PRIMARY KEY,
            total_stock INTEGER,
            remaining_stock INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wheel_spins (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            prize TEXT,
            created_at TEXT
        )
    """)
    
    # Initialize prizes stock if not already populated
    for name, stock in INITIAL_PRIZES:
        cur.execute("SELECT remaining_stock FROM wheel_prizes WHERE name = ?", (name,))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO wheel_prizes (name, total_stock, remaining_stock) VALUES (?, ?, ?)", (name, stock, stock))
            
    conn.commit()
    conn.close()

def log_user_activity(user_id: int, username: str, first_name: str, query: str = None):
    now_str = datetime.datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT search_count FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    
    if row is None:
        cur.execute("""
            INSERT INTO users (user_id, username, first_name, first_seen, last_seen, search_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username or "", first_name or "", now_str, now_str, 1 if query else 0))
    else:
        new_cnt = row[0] + (1 if query else 0)
        cur.execute("""
            UPDATE users SET username = ?, first_name = ?, last_seen = ?, search_count = ?
            WHERE user_id = ?
        """, (username or "", first_name or "", now_str, new_cnt, user_id))
        
    if query:
        cur.execute("INSERT INTO searches (user_id, query, timestamp) VALUES (?, ?, ?)", (user_id, query.lower().strip(), now_str))
        
    conn.commit()
    conn.close()

def get_statistics():
    now = datetime.datetime.now()
    fifteen_mins_ago = (now - datetime.timedelta(minutes=15)).isoformat()
    today_start = (now - datetime.timedelta(hours=24)).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (fifteen_mins_ago,))
    online_users = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (today_start,))
    active_24h = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM searches")
    total_searches = cur.fetchone()[0]
    
    cur.execute("""
        SELECT query, COUNT(*) as cnt 
        FROM searches 
        GROUP BY query 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    top_searches = cur.fetchall()
    
    cur.execute("""
        SELECT user_id, username, first_name, last_seen 
        FROM users 
        ORDER BY last_seen DESC 
        LIMIT 5
    """)
    recent_users = cur.fetchall()
    
    conn.close()
    
    return {
        "total_users": total_users,
        "online_users": online_users,
        "active_24h": active_24h,
        "total_searches": total_searches,
        "top_searches": top_searches,
        "recent_users": recent_users
    }

# --- ÇARXIFƏLƏK (WHEEL OF FORTUNE) LOGIC ---

def check_user_wheel_status(user_id: int):
    """Checks if user has already spun the wheel."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT prize, created_at FROM wheel_spins WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return True, row[0], row[1]
    return False, None, None

def get_wheel_stock_info():
    """Returns list of prizes and their remaining stock."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, total_stock, remaining_stock FROM wheel_prizes")
    rows = cur.fetchall()
    conn.close()
    return rows

def spin_wheel(user_id: int, username: str, first_name: str):
    """
    Executes a spin for the user.
    Total slots: 30.
    Prizes in slots based on remaining stock.
    Returns:
      (status: 'ALREADY_SPUN' | 'WIN' | 'LOSE', prize_name: str or None)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if already spun
    cur.execute("SELECT prize FROM wheel_spins WHERE user_id = ?", (user_id,))
    existing = cur.fetchone()
    if existing:
        conn.close()
        return "ALREADY_SPUN", existing[0]

    # Get remaining stock of prizes
    cur.execute("SELECT name, remaining_stock FROM wheel_prizes WHERE remaining_stock > 0")
    available_prizes = cur.fetchall()

    # Construct the 30-slot wheel
    # Available prize slots:
    slots = []
    for name, rem in available_prizes:
        # Add available items as slots
        slots.extend([name] * rem)
        
    # Cap slots to max 5 prize slots
    slots = slots[:5]
    
    # Fill remaining slots up to 30 with 'BOŞ'
    empty_slots_count = 30 - len(slots)
    slots.extend(["BOŞ"] * empty_slots_count)

    # Pick random slot
    selected_slot = random.choice(slots)
    now_str = datetime.datetime.now().isoformat()

    if selected_slot != "BOŞ":
        # WINNER!
        # Decrement remaining stock
        cur.execute("UPDATE wheel_prizes SET remaining_stock = remaining_stock - 1 WHERE name = ?", (selected_slot,))
        cur.execute("""
            INSERT INTO wheel_spins (user_id, username, first_name, prize, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username or "", first_name or "", selected_slot, now_str))
        conn.commit()
        conn.close()
        return "WIN", selected_slot
    else:
        # LOSE
        cur.execute("""
            INSERT INTO wheel_spins (user_id, username, first_name, prize, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username or "", first_name or "", None, now_str))
        conn.commit()
        conn.close()
        return "LOSE", None

def get_wheel_winners():
    """Returns list of all winners."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, username, first_name, prize, created_at 
        FROM wheel_spins 
        WHERE prize IS NOT NULL 
        ORDER BY created_at DESC
    """)
    winners = cur.fetchall()
    conn.close()
    return winners

def reset_user_wheel_spin(target_user_id: int):
    """Admin tool to reset spin for a user if needed."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM wheel_spins WHERE user_id = ?", (target_user_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

if __name__ == '__main__':
    init_db()
    print("Prizes in stock:", get_wheel_stock_info())
    st, pr = spin_wheel(9999999, "test_user", "Test", )
    print("Spin result:", st, pr)
    print("After spin stock:", get_wheel_stock_info())
    reset_user_wheel_spin(9999999)
