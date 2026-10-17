import os
import threading
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from scraper import search_all_sites
from database import init_db

load_dotenv()

def start_telegram_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("ℹ️ TELEGRAM_BOT_TOKEN təyin edilməyib. Yalnız Veb Tətbiq işləyir.")
        return

    try:
        from bot import run_bot
        print(f"🤖 Telegram Bot başladılır (Token: {token[:6]}***)...")
        run_bot(token)
    except Exception as e:
        print(f"❌ Telegram Bot xətası: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    yield

app = FastAPI(title="Qiymət Radar API", version="1.0.0", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/manifest.json")
async def manifest():
    return FileResponse("static/manifest.json")

@app.get("/api/search")
async def api_search(q: str = Query(..., min_length=1)):
    try:
        results = search_all_sites(q)
        return JSONResponse(content=results)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "Qiymət Radar"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Veb Tətbiq aktivdir: http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
