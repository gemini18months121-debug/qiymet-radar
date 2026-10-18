import os
import threading
import datetime
import requests
import uvicorn
from contextlib import asynccontextmanager
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

from scraper import search_all_sites
from database import (
    init_db,
    spin_wheel,
    check_user_wheel_status,
    check_device_wheel_status,
    get_wheel_stock_info,
    get_user_game_data,
    add_game_points,
    claim_game_reward,
    get_game_leaderboard
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8495554960")

def send_admin_telegram_alert(text: str):
    """Adminə dərhal Telegram bildirişi göndərir."""
    if not TOKEN or not ADMIN_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": ADMIN_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=8)
    except Exception as e:
        print(f"Admin bildiriş xətası: {e}")

def start_telegram_bot():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("ℹ️ TELEGRAM_BOT_TOKEN təyin edilməyib. Yalnız Veb Tətbiq işləyir.")
        return

    try:
        from bot import run_bot
        print(f"🤖 Telegram Bot başladılır (Token: {TOKEN[:6]}***)...")
        run_bot(TOKEN)
    except Exception as e:
        print(f"❌ Telegram Bot xətası: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    yield

app = FastAPI(title="Qiymət Radar API", version="2.0.0", lifespan=lifespan)

# Static files mount
app.mount("/static", StaticFiles(directory="static"), name="static")

# Models
class WheelSpinPayload(BaseModel):
    user_id: int
    username: Optional[str] = ""
    first_name: Optional[str] = ""
    device_id: Optional[str] = ""

class GameScorePayload(BaseModel):
    user_id: int
    username: Optional[str] = ""
    first_name: Optional[str] = ""
    score: int
    device_id: Optional[str] = ""

class GameClaimPayload(BaseModel):
    user_id: int
    username: Optional[str] = ""
    first_name: Optional[str] = ""
    chosen_product: str
    device_id: Optional[str] = ""

# --- WEB ROUTES ---

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/manifest.json")
async def manifest():
    return FileResponse("static/manifest.json")

@app.get("/wheel")
async def wheel_page():
    return FileResponse("static/wheel.html")

@app.get("/game")
async def game_page():
    return FileResponse("static/game.html")

# --- SEARCH API ---

@app.get("/api/search")
async def api_search(q: str = Query(..., min_length=1)):
    try:
        results = search_all_sites(q)
        return JSONResponse(content=results)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "Qiymət Radar & Çarxıfələk"}

# --- WHEEL API (ÇARXIFƏLƏK & ANTİ-FRAUD) ---

@app.get("/api/wheel/status")
async def wheel_status(user_id: int = Query(...), device_id: Optional[str] = Query(None)):
    has_spun, prize, spin_time, dev_id, ip = check_user_wheel_status(user_id)
    if has_spun:
        return {
            "has_spun": True,
            "prize": prize,
            "message": f"Siz artıq çarxı çevirmisiniz (Qazanılan: {prize or 'Uduşsuz'}). Hər hesaba yalnız 1 şans verilir."
        }
    
    if device_id:
        dev_used, dev_user_id = check_device_wheel_status(device_id)
        if dev_used and dev_user_id != user_id:
            return {
                "has_spun": True,
                "prize": None,
                "message": f"Bu cihazdan artıq ID: {dev_user_id} hesabı ilə istifadə olunub. Hər cihazdan yalnız 1 hesab iştirak edə bilər!"
            }

    stock = get_wheel_stock_info()
    return {"has_spun": False, "stock": stock}

@app.post("/api/wheel/spin")
async def wheel_spin(payload: WheelSpinPayload, request: Request):
    # Get client IP
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or request.client.host

    status, prize = spin_wheel(
        user_id=payload.user_id,
        username=payload.username,
        first_name=payload.first_name,
        device_id=payload.device_id,
        ip_address=client_ip
    )

    baku_tz = datetime.timezone(datetime.timedelta(hours=4))
    now_str = datetime.datetime.now(baku_tz).strftime('%H:%M • %d.%m.%Y')
    uname_str = f"(@{payload.username})" if payload.username else "(istifadəçi adı yoxdur)"

    if status == "WIN":
        # Send instant notification to Admin
        admin_alert = (
            "🚨 <b>YENİ ÇARXIFƏLƏK QALİBİ VAR!</b> 🎁\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Qalib:</b> {payload.first_name} {uname_str}\n"
            f"🆔 <b>Telegram ID:</b> <code>{payload.user_id}</code>\n"
            f"📱 <b>Cihaz ID:</b> <code>{payload.device_id[:16]}...</code>\n"
            f"🌐 <b>IP Ünvanı:</b> <code>{client_ip}</code>\n"
            f"🎁 <b>Qazandığı Endirim:</b> <b>{prize}</b>\n"
            f"🕒 <b>Vaxt:</b> {now_str}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 <a href=\"tg://user?id={payload.user_id}\">İstifadəçiyə yaz</a>"
        )
        send_admin_telegram_alert(admin_alert)
        return {"ok": True, "status": "WIN", "prize": prize}

    elif status == "LOSE":
        return {"ok": True, "status": "LOSE", "prize": None}

    elif status == "ALREADY_SPUN_USER":
        return {"ok": False, "status": "ERROR", "message": "Bu Telegram hesabından artıq çarx çevrilib!"}

    elif status == "ALREADY_SPUN_DEVICE":
        return {"ok": False, "status": "ERROR", "message": "Bu cihazdan artıq başqa bir Telegram hesabı ilə istifadə olunub!"}

    elif status == "IP_LIMIT_EXCEEDED":
        return {"ok": False, "status": "ERROR", "message": "Bu IP ünvanından gündəlik icazə verilən hədd bitib!"}

    return {"ok": False, "status": "ERROR", "message": "Gözlənilməz xəta baş verdi."}

# --- GAME API (OYUN & 100 XAL SİSTEMİ) ---

@app.get("/api/game/user")
async def game_user(user_id: int = Query(...)):
    data = get_user_game_data(user_id)
    return data

@app.post("/api/game/score")
async def game_score(payload: GameScorePayload, request: Request):
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or request.client.host
    new_points, total_earned = add_game_points(
        user_id=payload.user_id,
        username=payload.username,
        first_name=payload.first_name,
        points=payload.score,
        device_id=payload.device_id,
        ip_address=client_ip
    )
    return {"ok": True, "new_points": new_points, "total_earned": total_earned}

@app.post("/api/game/claim")
async def game_claim(payload: GameClaimPayload, request: Request):
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or request.client.host
    ok, msg, voucher_code = claim_game_reward(
        user_id=payload.user_id,
        username=payload.username,
        first_name=payload.first_name,
        chosen_product=payload.chosen_product,
        device_id=payload.device_id,
        ip_address=client_ip
    )

    if ok:
        baku_tz = datetime.timezone(datetime.timedelta(hours=4))
        now_str = datetime.datetime.now(baku_tz).strftime('%H:%M • %d.%m.%Y')
        uname_str = f"(@{payload.username})" if payload.username else "(istifadəçi adı yoxdur)"

        admin_alert = (
            "🎮 <b>OYUN QALİBİ BİLDİRİŞİ (100 XAL)!</b> 🏆\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Oyunçu:</b> {payload.first_name} {uname_str}\n"
            f"🆔 <b>Telegram ID:</b> <code>{payload.user_id}</code>\n"
            f"📱 <b>Cihaz ID:</b> <code>{payload.device_id[:16]}...</code>\n"
            f"🌐 <b>IP Ünvanı:</b> <code>{client_ip}</code>\n"
            f"🎁 <b>Seçdiyi Endirimli Hesab:</b> <b>{payload.chosen_product}</b>\n"
            f"🎟️ <b>Xüsusi Kupon Kodu:</b> <code>{voucher_code}</code>\n"
            f"🕒 <b>Vaxt:</b> {now_str}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 <a href=\"tg://user?id={payload.user_id}\">İstifadəçiyə yaz</a>"
        )
        send_admin_telegram_alert(admin_alert)

        user_data = get_user_game_data(payload.user_id)
        return {
            "ok": True,
            "voucher_code": voucher_code,
            "remaining_points": user_data["points"],
            "message": "Təbriklər! Kuponunuz yaradıldı."
        }
    else:
        return {"ok": False, "message": msg}

@app.get("/api/game/leaderboard")
async def game_leaderboard():
    board = get_game_leaderboard(limit=10)
    return {"leaderboard": board}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Veb Tətbiq aktivdir: http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
