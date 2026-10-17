import sqlite3
import datetime

DB_PATH = "stats.db"

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
    
    # Total users
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    # Online / Active right now (last 15 mins)
    cur.execute("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (fifteen_mins_ago,))
    online_users = cur.fetchone()[0]
    
    # Active in last 24h
    cur.execute("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (today_start,))
    active_24h = cur.fetchone()[0]
    
    # Total searches
    cur.execute("SELECT COUNT(*) FROM searches")
    total_searches = cur.fetchone()[0]
    
    # Top 5 searched products
    cur.execute("""
        SELECT query, COUNT(*) as cnt 
        FROM searches 
        GROUP BY query 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    top_searches = cur.fetchall()
    
    # Recent users
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

if __name__ == '__main__':
    init_db()
    log_user_activity(8495554960, "Zeka233", "Zəka", "spotify")
    print("Clean stats test:", get_statistics())
