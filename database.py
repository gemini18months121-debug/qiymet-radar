import sqlite3
import datetime
import random
import os

DB_PATH = "stats.db"

# 1. Yeni Çarxıfələk Hədiyyələri (Toplam 65 ədəd uduşlu xana, 200 boş xana = 265 xana)
NEW_PRIZES = [
    ("Youtube Premium (2.46 AZN - 2.96 yox)", 10),
    ("Spotify Premium (2.30 AZN - 2.70 yox)", 10),
    ("Netflix Premium 1 Ay (2.30 AZN - 2.72 yox)", 5),
    ("Gemini Pro 18 Ay (2.50 AZN - 3.00 yox)", 20),
    ("Capcut Pro 1 Ay (3.00 AZN - 3.50 yox)", 10),
    ("Capcut Pro 1 Ay 1600 Kredit (3.80 AZN - 4.80 yox)", 10),
]

TOTAL_WHEEL_SLOTS = 265

# 2. Oyun 100 Xal Mükafat Seçimləri
GAME_REWARD_OPTIONS = [
    "Youtube Premium (2.46 AZN - 2.96 yox)",
    "Spotify Premium (2.30 AZN - 2.70 yox)",
    "Netflix Premium 1 Ay (2.30 AZN - 2.72 yox)",
    "Gemini Pro 18 Ay (2.50 AZN - 3.00 yox)",
    "Capcut Pro 1 Ay (3.00 AZN - 3.50 yox)",
    "Capcut Pro 1 Ay 1600 Kredit (3.80 AZN - 4.80 yox)"
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # İstifadəçilər cədvəli
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
    
    # Axtarışlar jurnalı
    cur.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            timestamp TEXT
        )
    """)
    
    # Çarx hədiyyələri stoku
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wheel_prizes (
            name TEXT PRIMARY KEY,
            total_stock INTEGER,
            remaining_stock INTEGER
        )
    """)
    
    # Çarx fırlatmaları (Anti-Fraud: user_id, device_id, ip_address)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wheel_spins (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            prize TEXT,
            created_at TEXT,
            device_id TEXT,
            ip_address TEXT
        )
    """)
    
    # Mövcud bazaya sütunları əlavə et (əgər yoxdursa)
    try:
        cur.execute("ALTER TABLE wheel_spins ADD COLUMN device_id TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute("ALTER TABLE wheel_spins ADD COLUMN ip_address TEXT")
    except sqlite3.OperationalError:
        pass

    # Oyunçu xalları cədvəli
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            points INTEGER DEFAULT 0,
            total_earned INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            last_played TEXT,
            device_id TEXT,
            ip_address TEXT
        )
    """)

    # Oyundan qazanılan 100 xallıq endirim kuponları
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            chosen_product TEXT,
            points_spent INTEGER DEFAULT 100,
            voucher_code TEXT UNIQUE,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT,
            device_id TEXT,
            ip_address TEXT
        )
    """)
    
    # Yeni hədiyyələri bazaya yaz və ya mövcud olanları yenilə
    for name, stock in NEW_PRIZES:
        cur.execute("SELECT remaining_stock FROM wheel_prizes WHERE name = ?", (name,))
        row = cur.fetchone()
        if row is None:
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

# --- ÇARXIFƏLƏK LOGİSTİKASI & ANTİ-FRAUD ---

def check_user_wheel_status(user_id: int):
    """Yoxlayır: bu Telegram ID artıq çarx çeviribmi?"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT prize, created_at, device_id, ip_address FROM wheel_spins WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return True, row[0], row[1], row[2], row[3]
    return False, None, None, None, None

def check_device_wheel_status(device_id: str):
    """Yoxlayır: bu Cihaz (Fingerprint/UUID) artıq başqa hesab üçün istifadə edilibmi?"""
    if not device_id or not device_id.strip():
        return False, None
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, prize FROM wheel_spins WHERE device_id = ?", (device_id.strip(),))
    row = cur.fetchone()
    conn.close()
    if row:
        return True, row[0]
    return False, None

def get_wheel_stock_info():
    """Qalan hədiyyə stokunu qaytarır."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, total_stock, remaining_stock FROM wheel_prizes WHERE remaining_stock > 0")
    rows = cur.fetchall()
    conn.close()
    return rows

def spin_wheel(user_id: int, username: str, first_name: str, device_id: str = None, ip_address: str = None):
    """
    Çarxıfələk fırladılması.
    Cəmi xana: 265 ədəd.
    Mükafat xanaları: 65 ədəd (stok bitdikcə azalır).
    Boş xanalar: 200 ədəd (və ya 265 - qalan mükafatlar).
    
    Anti-Fraud Təhlükəsizlik Yoxlamaları:
    1. Telegram ID yoxlanışı (1 hesaba 1 şans)
    2. Cihaz ID (Device Fingerprint) yoxlanışı (1 telefona/kompüterə 1 şans)
    3. IP Ünvanı yoxlanışı (Eyni IP-dən 24 saatda maksimum 3 spin)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Telegram ID yoxlanışı
    cur.execute("SELECT prize FROM wheel_spins WHERE user_id = ?", (user_id,))
    existing_user = cur.fetchone()
    if existing_user:
        conn.close()
        return "ALREADY_SPUN_USER", existing_user[0]

    # 2. Cihaz ID (Fingerprint) yoxlanışı
    clean_device = (device_id or "").strip()
    if clean_device:
        cur.execute("SELECT user_id, prize FROM wheel_spins WHERE device_id = ?", (clean_device,))
        existing_dev = cur.fetchone()
        if existing_dev and existing_dev[0] != user_id:
            conn.close()
            return "ALREADY_SPUN_DEVICE", f"Bu cihazdan artıq ID: {existing_dev[0]} ilə istifadə olunub!"

    # 3. IP Ünvanı yoxlanışı (Şübhəli bot/proxy hücumlarının qarşısını almaq üçün 24 saatda limit 3)
    clean_ip = (ip_address or "").strip()
    if clean_ip and clean_ip not in ("127.0.0.1", "localhost", ""):
        cur.execute("""
            SELECT COUNT(*) FROM wheel_spins 
            WHERE ip_address = ? AND datetime(created_at) >= datetime('now', '-1 day')
        """, (clean_ip,))
        ip_count = cur.fetchone()[0]
        if ip_count >= 3:
            conn.close()
            return "IP_LIMIT_EXCEEDED", "Bu IP ünvanından gündəlik icazə verilən hədd (3 cəhd) bitib!"

    # Mövcud hədiyyələri götür
    cur.execute("SELECT name, remaining_stock FROM wheel_prizes WHERE remaining_stock > 0")
    available_prizes = cur.fetchall()

    # 265 xanalı çarxı qur
    slots = []
    for name, rem in available_prizes:
        slots.extend([name] * rem)
        
    # Qalan xanaları 265-ə qədər 'BOŞ' ilə doldur
    empty_slots_count = max(0, TOTAL_WHEEL_SLOTS - len(slots))
    slots.extend(["BOŞ"] * empty_slots_count)

    # Təsadüfi xananı seç
    selected_slot = random.choice(slots)
    now_str = datetime.datetime.now().isoformat()

    if selected_slot != "BOŞ":
        # QALİB OLDU!
        cur.execute("UPDATE wheel_prizes SET remaining_stock = remaining_stock - 1 WHERE name = ?", (selected_slot,))
        cur.execute("""
            INSERT INTO wheel_spins (user_id, username, first_name, prize, created_at, device_id, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username or "", first_name or "", selected_slot, now_str, clean_device, clean_ip))
        conn.commit()
        conn.close()
        return "WIN", selected_slot
    else:
        # BOŞ ÇIXDI (Uduşsuz)
        cur.execute("""
            INSERT INTO wheel_spins (user_id, username, first_name, prize, created_at, device_id, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username or "", first_name or "", None, now_str, clean_device, clean_ip))
        conn.commit()
        conn.close()
        return "LOSE", None

def get_wheel_winners():
    """Bütün çarx qaliblərini qaytarır."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, username, first_name, prize, created_at, device_id, ip_address 
        FROM wheel_spins 
        WHERE prize IS NOT NULL 
        ORDER BY created_at DESC
    """)
    winners = cur.fetchall()
    conn.close()
    return winners

def reset_user_wheel_spin(target_user_id: int):
    """Admin üçün istifadəçinin çarx statusunu sıfırlamaq funksiyası."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM wheel_spins WHERE user_id = ?", (target_user_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

# --- OYUN & XAL SİSTEMİ (100 XAL = 1 ENDİRİMLİ HESAB) ---

def get_user_game_data(user_id: int):
    """İstifadəçinin oyun xallarını və statistikasını qaytarır."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT points, total_earned, games_played, last_played 
        FROM game_users WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "points": row[0],
            "total_earned": row[1],
            "games_played": row[2],
            "last_played": row[3]
        }
    return {
        "points": 0,
        "total_earned": 0,
        "games_played": 0,
        "last_played": None
    }

def add_game_points(user_id: int, username: str, first_name: str, points: int, device_id: str = None, ip_address: str = None):
    """
    Oyundan qazanılan xalları balansa əlavə edir.
    Anti-Cheat: 1 raundda maksimum 35 xal qazanıla bilər.
    """
    valid_points = max(1, min(points, 35))
    now_str = datetime.datetime.now().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT points, total_earned, games_played FROM game_users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    
    if row is None:
        cur.execute("""
            INSERT INTO game_users (user_id, username, first_name, points, total_earned, games_played, last_played, device_id, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username or "", first_name or "", valid_points, valid_points, 1, now_str, device_id or "", ip_address or ""))
        new_balance = valid_points
        new_total = valid_points
    else:
        new_balance = row[0] + valid_points
        new_total = row[1] + valid_points
        new_played = row[2] + 1
        cur.execute("""
            UPDATE game_users 
            SET points = ?, total_earned = ?, games_played = ?, last_played = ?, username = ?, first_name = ?, device_id = ?, ip_address = ?
            WHERE user_id = ?
        """, (new_balance, new_total, new_played, now_str, username or "", first_name or "", device_id or "", ip_address or "", user_id))
        
    conn.commit()
    conn.close()
    return new_balance, new_total

def claim_game_reward(user_id: int, username: str, first_name: str, chosen_product: str, device_id: str = None, ip_address: str = None):
    """
    100 xalı istifadəçinin seçdiyi endirimli hesaba dəyişir.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT points FROM game_users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    
    if not row or row[0] < 100:
        conn.close()
        current_pts = row[0] if row else 0
        return False, f"Kifayət qədər xal yoxdur! Sizdə {current_pts} xal var, minimum 100 xal tələb olunur.", None
        
    # Unikal kupon kodu yarat (məsələn: UH-100X-7F2A)
    random_code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=5))
    voucher_code = f"UH-100X-{random_code}"
    now_str = datetime.datetime.now().isoformat()
    
    # 100 xal çıx
    new_points = row[0] - 100
    cur.execute("UPDATE game_users SET points = ? WHERE user_id = ?", (new_points, user_id))
    
    # Mükafatı qeyd et
    cur.execute("""
        INSERT INTO game_rewards (user_id, username, first_name, chosen_product, points_spent, voucher_code, status, created_at, device_id, ip_address)
        VALUES (?, ?, ?, ?, 100, ?, 'PENDING', ?, ?, ?)
    """, (user_id, username or "", first_name or "", chosen_product, voucher_code, now_str, device_id or "", ip_address or ""))
    
    conn.commit()
    conn.close()
    return True, "Mükafat uğurla aktivləşdirildi!", voucher_code

def get_game_leaderboard(limit: int = 10):
    """Oyun liderlər cədvəli."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, username, first_name, points, total_earned 
        FROM game_users 
        ORDER BY total_earned DESC 
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_game_rewards_list():
    """Bütün qazanılmış oyun kuponları."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, username, first_name, chosen_product, voucher_code, status, created_at, device_id, ip_address
        FROM game_rewards 
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
    print("Stock:", get_wheel_stock_info())
