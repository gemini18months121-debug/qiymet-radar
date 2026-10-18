import os
import re
import asyncio
import datetime
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from scraper import search_all_sites
from database import (
    init_db, log_user_activity, get_statistics,
    check_user_wheel_status, spin_wheel, get_wheel_stock_info, get_wheel_winners,
    get_user_game_data, add_game_points, claim_game_reward, get_game_leaderboard, get_game_rewards_list,
    GAME_REWARD_OPTIONS
)
from quiz_data import get_random_quiz_question, get_question_by_id

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8495554960")
WEBAPP_URL = os.getenv("WEBAPP_URL") or os.getenv("RENDER_EXTERNAL_URL") or "https://qiymet-radar.onrender.com"

USER_KEYBOARD = [
    ["🎬 Capcut Pro", "🪟 Windows 11 Pro"],
    ["🎨 Canva Pro", "💼 Microsoft 365"],
    ["🎵 Spotify", "🍿 Netflix 4K"],
    ["🎡 Çarxıfələk (265 Xana)", "🎮 3D Oyun & Xal"],
    ["🧠 Məntiq Sualı (+5 Xal)", "👑 Ucuzhesablar.com"],
    ["❓ Kömək"]
]

ADMIN_KEYBOARD = [
    ["🎬 Capcut Pro", "🪟 Windows 11 Pro"],
    ["🎨 Canva Pro", "💼 Microsoft 365"],
    ["🎵 Spotify", "🍿 Netflix 4K"],
    ["🎡 Çarxıfələk", "🎮 3D Oyun & Xal"],
    ["🧠 Məntiq Sualı", "📊 Statistika Paneli"],
    ["👑 Ucuzhesablar.com"]
]

TRACKED_PRODUCTS = [
    "Capcut Pro",
    "Windows 11 Pro",
    "Canva Pro",
    "Microsoft 365",
    "Netflix",
    "Spotify"
]

def generate_ad_text(product_name, duration, price, monthly_price):
    monthly_note = f" (Aylıq cəmi {monthly_price:.2f} AZN!)" if duration != "1 Ay" else ""
    return (
        f"🔥 <b>BAZARIN ƏN UCUZ QİYMƏTİ BİZDƏ!</b> 🔥\n\n"
        f"⚡ <b>Məhsul:</b> {product_name}\n"
        f"📅 <b>Müddət:</b> {duration}\n"
        f"💰 <b>QİYMƏT:</b> <code>{price:.2f} AZN</code>{monthly_note}\n\n"
        f"✅ 100% Rəsmi və Zəmanətli çıxış\n"
        f"✅ Ani və avtomatik çatdırılma\n"
        f"🚀 Bütün digər 22 mağazadan daha sərfəli!\n\n"
        f"🌐 <b>Saytımızdan birbaşa sifariş:</b> https://ucuzhesablar.com\n"
        f"📲 <b>WhatsApp ilə sifariş:</b> https://wa.me/994773026579"
    )

def build_stats_message():
    stats = get_statistics()
    stock_info = get_wheel_stock_info()
    winners = get_wheel_winners()
    rewards = get_game_rewards_list()
    
    baku_tz = datetime.timezone(datetime.timedelta(hours=4))
    now = datetime.datetime.now(baku_tz).strftime('%H:%M:%S • %d.%m.%Y')

    stock_text = ""
    for name, total, rem in stock_info:
        stock_text += f"   • {name}: <code>{rem}/{total} qalıb</code>\n"

    top_text = ""
    if stats['top_searches']:
        for i, (q, count) in enumerate(stats['top_searches'], 1):
            top_text += f"   {i}. <b>{q.capitalize()}</b> — <code>{count} dəfə</code>\n"
    else:
        top_text = "   <i>Hələ axtarış qeydə alınmayıb</i>\n"

    recent_text = ""
    if stats['recent_users']:
        for u in stats['recent_users']:
            uid, uname, fname, lseen = u
            name_display = fname or uname or f"İstifadəçi {uid}"
            uname_display = f"(@{uname})" if uname else ""
            recent_text += f"   • <b>{name_display}</b> {uname_display}\n"
    else:
        recent_text = "   <i>İstifadəçi tapılmadı</i>\n"

    msg = (
        "📊 <b>QIYMƏT RADAR — STATİSTİKA VƏ NƏZARƏT PANELİ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Toplam İstifadəçi:</b> <code>{stats['total_users']} nəfər</code>\n"
        f"🟢 <b>Hal-hazırda Aktiv (Online):</b> <code>{stats['online_users']} nəfər</code> <i>(son 15 dəqiqə)</i>\n"
        f"⚡ <b>Son 24 saatda Aktiv:</b> <code>{stats['active_24h']} nəfər</code>\n"
        f"🔍 <b>Toplam Axtarış Sayı:</b> <code>{stats['total_searches']} dəfə</code>\n\n"
        "🎡 <b>Çarxıfələk Vəziyyəti (265 Xana / 65 Hədiyyə):</b>\n"
        f"   🏆 Çarx qalibləri: <code>{len(winners)} nəfər</code>\n"
        f"{stock_text}\n"
        "🎮 <b>Oyun & Kupon Vəziyyəti:</b>\n"
        f"   🎁 Verilən 100 Xallıq Kuponlar: <code>{len(rewards)} ədəd</code>\n\n"
        "📈 <b>Ən Çox Axtarılan Məhsullar (Top 5):</b>\n"
        f"{top_text}\n"
        "👤 <b>Son Aktiv İstifadəçilər:</b>\n"
        f"{recent_text}"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 <i>Yenilənmə: {now} (Bakı vaxtı)</i>"
    )
    return msg

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username, user.first_name)

    is_admin = (str(user.id) == str(ADMIN_CHAT_ID))
    kb = ADMIN_KEYBOARD if is_admin else USER_KEYBOARD
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)

    msg = (
        "👋 <b>Salam! Qiymət Radar Botuna xoş gəlmisiniz.</b>\n\n"
        "👑 <b>Ucuzhesablar.com</b> və Azərbaycanın <b>22 əsas rəqəmsal satış saytını</b> "
        "eyni anda analiz edib <b>ən sərfəli qiyməti</b> tapıram.\n\n"
        "🎡 <b>265 Xanalı Çarxıfələk:</b> «🎡 Çarxıfələk» bölməsində şansınızı yoxlayaraq 65 xüsusi endirimli hesabdan birini qazanın!\n\n"
        "🎮 <b>3D Məhsul Ovçusu Oyunu:</b> «🎮 3D Oyun & Xal» bölməsində 3D qəhrəmanı idarə edib xal toplayın və 100 xala İSTƏDİYİNİZ hesabı endirimlə əldə edin!\n\n"
        "🧠 <b>100 Məntiq Sualı:</b> «🧠 Məntiq Sualı» bölməsində suallara düzgün cavab verərək hər suala +5 xal qazanın!\n\n"
        "🔍 <b>Axtarış üçün:</b>\n"
        "• Sadəcə məhsulun adını yazın (məs: <code>Capcut</code>, <code>Spotify</code>, <code>Canva</code>)\n"
        "• Və ya <code>/search &lt;məhsul&gt;</code> əmrindən istifadə edin."
    )
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username, user.first_name)
    text = (
        "ℹ️ <b>Botdan İstifadə Qaydaları:</b>\n\n"
        "1. <b>23 Saytda Dəqiq Axtarış:</b> <code>/search Canva Pro</code> və ya birbaşa məhsul adını yazın.\n"
        "2. <b>Ağıllı Aylıq Müqayisə:</b> Tək məbləğə deyil, aylıq maya dəyərinə görə ən sərfəli təklif hesablanır.\n"
        "3. <b>🎡 265 Xanalı Çarxıfələk:</b> Hər cihazdan yalnız 1 hesab çarx çevirə bilər (Telegram ID + Cihaz ID + IP qorunması).\n"
        "4. <b>🎮 3D Məhsul Ovçusu:</b> 3D oyunda loqoları tutaraq xal toplayın və bombalardan qaçın!\n"
        "5. <b>🧠 100 Məntiq Sualı:</b> Maarifləndirici 100 ədəd 3 variantlı suala cavab verərək hər suala +5 xal qazanın!\n"
        "6. <b>🎁 100 Xal Mükafatı:</b> 100 xalı tamamlayaraq 6 premium hesabdan istədiyinizi xüsusi endirimlə götürün!\n"
        "7. <b>Birbaşa Keçid:</b> Nəticənin altındakı düymə ilə birbaşa Ucuzhesablar.com-dan sifariş edə bilərsiniz."
    )
    await update.message.reply_text(text, parse_mode='HTML')

async def website_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👑 <b>Ucuzhesablar.com — Azərbaycanın Ən Ucuz Rəqəmsal Mağazası</b>\n\n"
        "🌐 <b>Sayt:</b> https://ucuzhesablar.com\n"
        "📲 <b>WhatsApp:</b> https://wa.me/994773026579\n\n"
        "⚡ Bütün premium proqramlar, lisenziyalar və oyun hesabları ən sərfəli qiymətlərlə!"
    )
    await update.message.reply_text(text, parse_mode='HTML')

async def wheel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wheel of Fortune entrypoint."""
    user = update.effective_user
    log_user_activity(user.id, user.username, user.first_name)

    has_spun, prize, spin_time, dev_id, ip = check_user_wheel_status(user.id)
    if has_spun:
        if prize:
            msg = (
                f"⛔ <b>Siz artıq çarxı çevirmisiniz!</b>\n\n"
                f"🎉 Qazandığınız endirim: <b>{prize}</b> 🎁\n\n"
                f"✅ Hədiyyənizi aktivləşdirmək üçün Adminlə əlaqə saxlayın:\n"
                f"👤 Admin: @Zeka233\n"
                f"📲 WhatsApp: https://wa.me/994773026579\n"
                f"🆔 Sizin Telegram ID: <code>{user.id}</code>"
            )
        else:
            msg = (
                "⛔ <b>Siz artıq çarxı çevirmisiniz!</b>\n\n"
                "😢 Təəssüf ki, çarx uduşsuz xanada dayanmışdı. Hər istifadəçinin sistemdə <b>yalnız 1 dəfə</b> şansı var.\n\n"
                "🎮 <b>Amma zəmanətli endirim qazanmaq şansınız var!</b>\n"
                "«🎮 3D Oyun & Xal» bölməsində 3D oyunu oynayaraq və ya məntiq suallarını cavablandıraraq 100 xal toplayın və istədiyiniz hesabı endirimlə əldə edin!\n\n"
                "🛍️ Saytımız: https://ucuzhesablar.com"
            )
        webapp_game_url = f"{WEBAPP_URL}/game"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 3D Oyuna Keç (100 Xal Yığ)", web_app=WebAppInfo(url=webapp_game_url))]
        ])
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=kb)
        return

    stock_info = get_wheel_stock_info()
    stock_lines = ""
    for name, total, rem in stock_info:
        stock_lines += f"• 🎁 <b>{name}</b> — <i>{rem} ədəd qalıb</i>\n"

    msg = (
        "🎡 <b>UCUZHESABLAR.COM — BÖYÜK ÇARXIFƏLƏK!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Şansınızı yoxlayın və premium hesabları xüsusi endirimlə qazanın!\n\n"
        "🏆 <b>Mövcud Uduşlu Hədiyyələr (Toplam 65 Ədəd):</b>\n"
        f"{stock_lines}\n"
        "🎯 <b>Şərtlər və Anti-Fraud Qaydaları:</b>\n"
        "• Çarxın toplam <b>265 xanası</b> var (65 uduşlu + 200 boş).\n"
        "• <b>Təhlükəsizlik:</b> Sui-istifadələrin qarşısını almaq üçün sistem həm <b>Telegram ID</b>, həm də <b>Cihaz ID</b> və <b>IP ünvanını</b> yoxlayır.\n"
        "• Hər cihazdan və hesabdan <b>yalnız 1 dəfə</b> çarx fırladıla bilər.\n\n"
        "👇 <i>Şansınızı yoxlamaq üçün aşağıdakı düyməyə basın:</i>"
    )

    webapp_wheel_url = f"{WEBAPP_URL}/wheel"
    webapp_game_url = f"{WEBAPP_URL}/game"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎡 Çarxı Aç & Fırlat (Mini App)", web_app=WebAppInfo(url=webapp_wheel_url))],
        [InlineKeyboardButton("🎰 Çatda Birbaşa Fırlat", callback_data="spin_wheel")],
        [InlineKeyboardButton("🎮 3D Oyuna Keç (100 Xal Yığ)", web_app=WebAppInfo(url=webapp_game_url))]
    ])
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=kb)

async def game_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Game and points center."""
    user = update.effective_user
    log_user_activity(user.id, user.username, user.first_name)

    data = get_user_game_data(user.id)
    points = data["points"]

    msg = (
        "🎮 <b>UCUZHESABLAR — 3D MƏHSUL OVÇUSU OYUNU</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"⭐ <b>Sizin Cari Xalınız:</b> <code>{points} / 100 XAL</code>\n"
        f"🕹️ <b>Oynanılan Oyun:</b> <code>{data['games_played']} dəfə</code>\n\n"
        "🎯 <b>Oyun Qaydası:</b>\n"
        "Ortadakı 3D qəhrəmanı sağa-sola çəkərək göydən yağan premium loqoları (YouTube, Gemini, Capcut, Spotify, Canva, Duolingo, Netflix) tutun! Bombalardan qaçın!\n\n"
        "🏆 <b>100 Xal = 1 Endirimli Hesab Seçimi:</b>\n"
        "100 Xal topladıqda aşağıdakı 6 hesabdan <b>İSTƏDİYİNİZ 1 DƏNƏSİNİ</b> endirimlə əldə edə bilərsiniz!\n\n"
        "🎁 <b>Seçilə Bilən Endirimli Hesablar:</b>\n"
        "• 🎬 <b>Netflix Premium 1 Ay</b> — 2.30 AZN <i>(2.72 yox)</i>\n"
        "• ▶️ <b>YouTube Premium</b> — 2.46 AZN <i>(2.96 yox)</i>\n"
        "• 🎵 <b>Spotify Premium</b> — 2.30 AZN <i>(2.70 yox)</i>\n"
        "• 🤖 <b>Gemini Pro 18 Ay</b> — 2.50 AZN <i>(3.00 yox)</i>\n"
        "• ✂️ <b>CapCut Pro 1 Ay</b> — 3.00 AZN <i>(3.50 yox)</i>\n"
        "• ⚡ <b>CapCut Pro 1600 Kredit</b> — 3.80 AZN <i>(4.80 yox)</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👇 <i>Oyuna başlamaq və ya məntiq sualı cavablamaq üçün seçin:</i>"
    )

    webapp_game_url = f"{WEBAPP_URL}/game"
    buttons = [
        [InlineKeyboardButton("🎮 3D Oyunu Başlat (Mini App)", web_app=WebAppInfo(url=webapp_game_url))],
        [InlineKeyboardButton("🧠 Məntiq Sualı Cavabla (+5 Xal)", callback_data="game_quiz")]
    ]
    if points >= 100:
        buttons.append([InlineKeyboardButton("🎁 100 Xalı Endirimli Hesaba Dəyiş!", callback_data="game_claim_menu")])
    buttons.append([InlineKeyboardButton("🏆 Liderlər Cədvəli", callback_data="game_leaders")])

    kb = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=kb)

async def quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct in-chat 100 logic questions quiz entrypoint."""
    user = update.effective_user
    log_user_activity(user.id, user.username, user.first_name)

    q = get_random_quiz_question()
    quiz_text = (
        f"🧠 <b>MƏNTİQ VƏ BİLİK VİKTORİNASI (+5 XAL)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Sual #{q['id']}:</b>\n"
        f"{q['q']}\n\n"
        f"<b>A)</b> {q['a']}\n"
        f"<b>B)</b> {q['b']}\n"
        f"<b>C)</b> {q['c']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <i>Düzgün variantı seçin:</i>"
    )
    buttons = [
        [
            InlineKeyboardButton("A", callback_data=f"qans:{q['id']}:A"),
            InlineKeyboardButton("B", callback_data=f"qans:{q['id']}:B"),
            InlineKeyboardButton("C", callback_data=f"qans:{q['id']}:C")
        ],
        [InlineKeyboardButton("🔄 Başqa Sual", callback_data="game_quiz")],
        [InlineKeyboardButton("🎮 3D Oyunu Aç (Mini App)", web_app=WebAppInfo(url=f"{WEBAPP_URL}/game"))]
    ]
    await update.message.reply_text(quiz_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))

async def stat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_CHAT_ID):
        await update.message.reply_text("⛔ Bu panel yalnız Admin üçündür.")
        return

    msg = build_stats_message()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Məlumatları Yenilə", callback_data="refresh_stats")]
    ])
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=kb)

async def winners_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to list all wheel winners."""
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_CHAT_ID):
        await update.message.reply_text("⛔ Bu əmr yalnız Admin üçündür.")
        return

    winners = get_wheel_winners()
    if not winners:
        await update.message.reply_text("ℹ️ Hələlik çarxıfələkdə heç bir qalib yoxdur.")
        return

    lines = ["🏆 <b>ÇARXIFƏLƏK QALİBLƏRİ SİYAHISI:</b>\n━━━━━━━━━━━━━━━━━━━━"]
    for i, (uid, uname, fname, prize, dt, dev, ip) in enumerate(winners, 1):
        uname_str = f"(@{uname})" if uname else ""
        dev_short = f"Cihaz: {dev[:8]}..." if dev else "Çatdan"
        lines.append(
            f"{i}. <b>{fname}</b> {uname_str}\n"
            f"   🎁 Endirim: <b>{prize}</b>\n"
            f"   🆔 ID: <code>{uid}</code> • {dev_short}\n"
            f"   💬 <a href=\"tg://user?id={uid}\">İstifadəçiyə yaz</a>\n"
        )
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    await update.message.reply_text("\n".join(lines), parse_mode='HTML')

async def game_rewards_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to list claimed game vouchers."""
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_CHAT_ID):
        await update.message.reply_text("⛔ Bu əmr yalnız Admin üçündür.")
        return

    rewards = get_game_rewards_list()
    if not rewards:
        await update.message.reply_text("ℹ️ Hələlik 100 xal toplayıb kupon götürən oyunçu yoxdur.")
        return

    lines = ["🎮 <b>100 XAL OYUN KUPONLARI:</b>\n━━━━━━━━━━━━━━━━━━━━"]
    for i, r in enumerate(rewards, 1):
        rid, uid, uname, fname, prod, code, st, dt, dev, ip = r
        uname_str = f"(@{uname})" if uname else ""
        lines.append(
            f"{i}. <b>{fname}</b> {uname_str} (ID: <code>{uid}</code>)\n"
            f"   🎁 Məhsul: <b>{prod}</b>\n"
            f"   🎟️ Kupon: <code>{code}</code>\n"
            f"   💬 <a href=\"tg://user?id={uid}\">İstifadəçiyə yaz</a>\n"
        )
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    await update.message.reply_text("\n".join(lines), parse_mode='HTML')

async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args).strip() if context.args else ""
    if not query:
        await update.message.reply_text(
            "⚠️ Zəhmət olmasa axtarmaq istədiyiniz məhsulu qeyd edin.\n"
            "Məsələn: <code>/search Spotify</code> və ya <code>/search Canva Pro</code>",
            parse_mode='HTML'
        )
        return
    await execute_search(update, query)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text.strip()
    
    if raw_text == "❓ Kömək":
        await help_cmd(update, context)
        return
    elif raw_text == "👑 Ucuzhesablar.com":
        await website_cmd(update, context)
        return
    elif raw_text == "📊 Statistika Paneli":
        await stat_cmd(update, context)
        return
    elif "çarx" in raw_text.lower() or "carx" in raw_text.lower():
        await wheel_cmd(update, context)
        return
    elif "oyun" in raw_text.lower() or "xal" in raw_text.lower():
        await game_cmd(update, context)
        return
    elif "sual" in raw_text.lower() or "məntiq" in raw_text.lower() or "mentiq" in raw_text.lower():
        await quiz_cmd(update, context)
        return

    # Clean emojis (e.g. "🎬 Capcut Pro" -> "Capcut Pro")
    clean_query = re.sub(r'[^\w\s\+\-\.]', '', raw_text).strip()
    if not clean_query:
        clean_query = raw_text

    await execute_search(update, clean_query)

async def execute_search(update: Update, query: str):
    user = update.effective_user
    log_user_activity(user.id, user.username, user.first_name, query)

    wait_msg = await update.message.reply_text(
        f"🔍 <b>«{query}»</b> üzrə 23 mağazada dəqiq axtarış edilir...\n<i>Zəhmət olmasa gözləyin (2-4 saniyə)...</i>",
        parse_mode='HTML'
    )

    try:
        data = search_all_sites(query)

        if not data['items']:
            await wait_msg.edit_text(
                f"❌ <b>«{query}»</b> üzrə 23 mağazada heç bir elan tapılmadı.\nZəhmət olmasa adı dəqiqləşdirib təkrar yazın.",
                parse_mode='HTML'
            )
            return

        is_owner_cheapest = data.get('is_owner_cheapest', False)
        owner_best = data.get('owner_best')
        owner_url = data.get('owner_product_url', 'https://ucuzhesablar.com')
        cheapest_item = data['cheapest_item']

        lines = [
            f"🎯 <b>Məhsul Axtarışı:</b> <code>{query}</code>",
            "━━━━━━━━━━━━━━━━━━━━"
        ]

        if is_owner_cheapest and owner_best:
            lines.append(f"👑 <b>ƏN SƏRFƏLİ BİZDƏDİR (ucuzhesablar.com)!</b> 🥇")
            if owner_best['duration'] != "1 Ay":
                lines.append(f"💡 Bizdə <b>{owner_best['duration']}</b> cəmi <code>{owner_best['price']:.2f} AZN</code> (Aylıq: <b>{owner_best['monthly_price']:.2f} ₼</b>)!")
                comp_items = [it for it in data['items'] if not it.get('is_owner')]
                if comp_items:
                    comp = comp_items[0]
                    lines.append(f"<i>(Rəqibdə {comp['site']}: {comp['duration']} üçün {comp['price']:.2f} ₼, yəni aylıq {comp['monthly_price']:.2f} ₼)</i>")
            else:
                lines.append(f"💰 Bizim qiymət: <code>{owner_best['price']:.2f} AZN</code> ({owner_best['duration']})")
        else:
            lines.append(f"🏆 <b>Ən Sərfəli Təklif:</b> <code>{cheapest_item['price']:.2f} AZN</code> ({cheapest_item['duration']} — {cheapest_item['site']})")
            lines.append(f"📊 Aylıq maya dəyəri: <b>{cheapest_item['monthly_price']:.2f} AZN/ay</b>")
            if owner_best:
                lines.append(f"👑 Bizim qiymət: <code>{owner_best['price']:.2f} AZN</code> ({owner_best['duration']} — aylıq {owner_best['monthly_price']:.2f} ₼)")

        lines.append(f"━━━━━━━━━━━━━━━━━━━━\n📊 <b>Tapılan Dəqiq Elanlar ({data['total_found']} nəticə / 23 sayt):</b>\n")

        for i, item in enumerate(data['items'][:8], 1):
            is_owner = item.get('is_owner', False)
            site_tag = "👑 <b>ucuzhesablar.com (Bizim Sayt)</b>" if is_owner else f"🏬 <b>{item['site']}</b>"
            top_badge = " 🥇 (Ən Sərfəli)" if i == 1 else ""

            unit_note = ""
            if item['duration'] not in ["1 Ay"]:
                unit_note = f" <i>(Aylıq: {item['monthly_price']:.2f} ₼)</i>"

            lines.append(
                f"{i}. {site_tag}{top_badge}\n"
                f"   📌 <b>Elan:</b> {item['title']}\n"
                f"   📅 <b>Müddət:</b> <code>{item['duration']}</code>\n"
                f"   💵 <b>Qiymət:</b> <code>{item['price']:.2f} AZN</code>{unit_note}\n"
                f"   🔗 <a href=\"{item['url']}\">Elana bax →</a>\n"
            )

        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("⚡ <i>Ucuzhesablar.com • 23 Sayt Üzrə Radar</i>")

        inline_buttons = [
            [InlineKeyboardButton("🛍️ Məhsulu Sifariş Et (Ucuzhesablar.com)", url=owner_url)]
        ]

        # Hazır satış mətni (Yalnız Admin)
        user_id = str(update.effective_user.id)
        if user_id == str(ADMIN_CHAT_ID):
            ad_target = owner_best if owner_best else cheapest_item
            btn_dur = ad_target.get('duration', '1 Ay')
            btn_price = ad_target.get('price', 0)
            btn_monthly = ad_target.get('monthly_price', 0)
            inline_buttons.append([
                InlineKeyboardButton("📝 Hazır Satış Mətnini Al (Admin)", callback_data=f"ad:{query[:18]}:{btn_dur}:{btn_price}:{btn_monthly}")
            ])

        await wait_msg.edit_text(
            "\n".join(lines),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(inline_buttons),
            disable_web_page_preview=True
        )

    except Exception as e:
        await wait_msg.edit_text(f"⚠️ Xəta baş verdi: {str(e)}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    user_id = str(user.id)

    # 1. Refresh stats (Admin)
    if query.data == "refresh_stats":
        if user_id != str(ADMIN_CHAT_ID):
            await query.message.reply_text("⛔ Bu panel yalnız Admin üçündür.")
            return
        msg = build_stats_message()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Məlumatları Yenilə", callback_data="refresh_stats")]
        ])
        await query.message.edit_text(msg, parse_mode='HTML', reply_markup=kb)
        return

    # 2. Ad text (Admin)
    if query.data.startswith("ad:"):
        if user_id != str(ADMIN_CHAT_ID):
            await query.message.reply_text("⛔ Bu funksiya yalnız Admin üçündür.")
            return

        parts = query.data.split(":")
        prod_name = parts[1]
        duration = parts[2]
        price = float(parts[3])
        monthly_price = float(parts[4])

        ad_msg = generate_ad_text(prod_name, duration, price, monthly_price)
        reply = (
            "📋 <b>WhatsApp və Sosial Şəbəkələr Üçün Hazır Satış Mətni:</b>\n"
            "<i>(Aşağıdakı mətni kopyalayıb birbaşa paylaşa bilərsiniz)</i>\n\n"
            f"<code>{ad_msg}</code>"
        )
        await query.message.reply_text(reply, parse_mode='HTML', disable_web_page_preview=True)
        return

    # 3. Spin Wheel callback (Direct in-chat fallback)
    if query.data == "spin_wheel":
        has_spun, prev_prize, _, _, _ = check_user_wheel_status(user.id)
        if has_spun:
            await query.message.reply_text(
                "⛔ <b>Siz artıq çarxı çevirmisiniz!</b> Hər istifadəçinin və cihazın yalnız 1 şansı var.",
                parse_mode='HTML'
            )
            return

        await query.message.edit_text(
            "🎰 <b>Çarx fırlanır...</b> 🎡\n\n"
            "<code>[ ░░░░░░░░░░ ] 25%</code>\n"
            "<i>265 xana arasında bəxtiniz yoxlanılır...</i>",
            parse_mode='HTML'
        )
        await asyncio.sleep(1.0)

        await query.message.edit_text(
            "🎰 <b>Çarx fırlanır...</b> 🎯\n\n"
            "<code>[ ██████████ ] 100%</code>\n"
            "<i>Nəticə təyin edilir...</i>",
            parse_mode='HTML'
        )
        await asyncio.sleep(0.8)

        status, prize_won = spin_wheel(user.id, user.username, user.first_name, device_id="telegram_chat", ip_address="")

        if status == "WIN" and prize_won:
            win_msg = (
                f"🎉 <b>TƏBRİKLƏR! SİZ QALİB OLDUNUZ!</b> 🎁\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🏆 Qazandığınız Endirim: <b>{prize_won}</b>!\n\n"
                f"✅ Endiriminizi aktivləşdirmək və hesabı təhvil almaq üçün Adminlə əlaqə saxlayın:\n"
                f"👤 <b>Admin:</b> @Zeka233\n"
                f"📲 <b>WhatsApp:</b> https://wa.me/994773026579\n"
                f"🆔 <b>Sizin Telegram ID:</b> <code>{user.id}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 https://ucuzhesablar.com"
            )
            await query.message.edit_text(win_msg, parse_mode='HTML')

            if ADMIN_CHAT_ID:
                baku_tz = datetime.timezone(datetime.timedelta(hours=4))
                now_str = datetime.datetime.now(baku_tz).strftime('%H:%M • %d.%m.%Y')
                uname_str = f"(@{user.username})" if user.username else "(istifadəçi adı yoxdur)"
                
                admin_alert = (
                    "🚨 <b>YENİ ÇARXIFƏLƏK QALİBİ VAR!</b> 🎁\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>Qalib:</b> {user.first_name} {uname_str}\n"
                    f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n"
                    f"📱 <b>Mənbə:</b> Telegram Çatı\n"
                    f"🎁 <b>Qazandığı Endirim:</b> <b>{prize_won}</b>\n"
                    f"🕒 <b>Vaxt:</b> {now_str}\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"💬 <a href=\"tg://user?id={user.id}\">İstifadəçiyə yaz</a>"
                )
                try:
                    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_alert, parse_mode='HTML')
                except Exception as e:
                    print(f"Admin alert err: {e}")

        elif status == "LOSE":
            lose_msg = (
                "😢 <b>Təəssüf ki, çarx boş xanada dayandı!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "265 xana arasında bu dəfə bəxtiniz gətirmədi. Hər istifadəçi üçün yalnız 1 dəfə çarx çevirmək limiti var.\n\n"
                "🎮 <b>Amma zəmanətli endirim qazana bilərsiniz!</b>\n"
                "«🎮 3D Oyun & Xal» bölməsində 3D oyunu oynayaraq və ya məntiq suallarını cavablandıraraq 100 xal toplayın və İSTƏDİYİNİZ hesabı endirimlə götürün!\n\n"
                "🌐 <b>Saytımız:</b> https://ucuzhesablar.com\n"
                "📲 <b>WhatsApp:</b> https://wa.me/994773026579"
            )
            await query.message.edit_text(lose_msg, parse_mode='HTML')
        else:
            await query.message.edit_text(
                "⛔ <b>Siz artıq çarxı çevirmisiniz!</b> Hər istifadəçinin yalnız 1 şansı var.",
                parse_mode='HTML'
            )
        return

    # 4. In-chat Quiz with 100 Logic Questions
    if query.data == "game_quiz":
        q = get_random_quiz_question()
        quiz_text = (
            f"🧠 <b>MƏNTİQ VƏ BİLİK VİKTORİNASI (+5 XAL)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 <b>Sual #{q['id']}:</b>\n"
            f"{q['q']}\n\n"
            f"<b>A)</b> {q['a']}\n"
            f"<b>B)</b> {q['b']}\n"
            f"<b>C)</b> {q['c']}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 <i>Düzgün variantı seçin:</i>"
        )
        buttons = [
            [
                InlineKeyboardButton("A", callback_data=f"qans:{q['id']}:A"),
                InlineKeyboardButton("B", callback_data=f"qans:{q['id']}:B"),
                InlineKeyboardButton("C", callback_data=f"qans:{q['id']}:C")
            ],
            [InlineKeyboardButton("🔄 Başqa Sual Ver", callback_data="game_quiz")],
            [InlineKeyboardButton("🎮 3D Oyunu Aç (Mini App)", web_app=WebAppInfo(url=f"{WEBAPP_URL}/game"))]
        ]
        await query.message.reply_text(quiz_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(buttons))
        return

    if query.data.startswith("qans:"):
        parts = query.data.split(":")
        qid = int(parts[1])
        chosen = parts[2]
        q = get_question_by_id(qid)

        is_correct = (chosen == q["correct"])
        u_data = get_user_game_data(user.id)
        current_pts = u_data["points"]

        if is_correct:
            new_pts, _ = add_game_points(user.id, user.username, user.first_name, 5, "telegram_quiz", "")
            ans_msg = (
                f"🎉 <b>DÜZGÜN CAVAB! (+5 XAL QAZANDINIZ)</b> 👏\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ <b>Düzgün Variant:</b> <b>{q['correct']})</b> {q[q['correct'].lower()]}\n\n"
                f"💡 <b>Maarifləndirici İzah:</b>\n"
                f"<i>{q['exp']}</i>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"⭐ <b>Sizin Cari Xalınız:</b> <code>{new_pts} / 100 XAL</code>\n"
                f"{'🏆 <b>100 xalınız tamamlandı!</b> İndi istədiyiniz hesabı endirimlə seçə bilərsiniz!' if new_pts >= 100 else '100 xal toplayaraq istədiyiniz hesabı endirimlə əldə edin!'}"
            )
            next_buttons = [
                [InlineKeyboardButton("➡️ Növbəti Məntiq Sualı (+5 Xal)", callback_data="game_quiz")],
                [InlineKeyboardButton("🎮 3D Oyuna Keç", web_app=WebAppInfo(url=f"{WEBAPP_URL}/game"))]
            ]
            if new_pts >= 100:
                next_buttons.insert(0, [InlineKeyboardButton("🎁 100 Xalı Hesaba Dəyiş!", callback_data="game_claim_menu")])
            await query.message.edit_text(ans_msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(next_buttons))
        else:
            ans_msg = (
                f"❌ <b>TƏƏSSÜF Kİ, SƏHV CAVAB!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Sizin seçiminiz: <b>{chosen}</b>\n"
                f"✅ <b>Düzgün Variant:</b> <b>{q['correct']})</b> {q[q['correct'].lower()]}\n\n"
                f"💡 <b>Maarifləndirici İzah:</b>\n"
                f"<i>{q['exp']}</i>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"⭐ <b>Cari Xalınız:</b> <code>{current_pts} / 100 XAL</code>"
            )
            retry_buttons = [
                [InlineKeyboardButton("🔄 Başqa Sualı Sına", callback_data="game_quiz")],
                [InlineKeyboardButton("🎮 3D Oyuna Keç", web_app=WebAppInfo(url=f"{WEBAPP_URL}/game"))]
            ]
            await query.message.edit_text(ans_msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(retry_buttons))
        return

    # 5. Game Claim Menu
    if query.data == "game_claim_menu":
        u_data = get_user_game_data(user.id)
        if u_data["points"] < 100:
            await query.message.reply_text(
                f"⚠️ <b>Kifayət qədər xalınız yoxdur!</b>\nSizdə cəmi <code>{u_data['points']}</code> xal var. Minimum <b>100 Xal</b> lazımdır.\nOyunu oynayaraq və ya məntiq suallarına cavab verərək xal toplayın!",
                parse_mode='HTML'
            )
            return

        claim_buttons = [
            [InlineKeyboardButton("🎬 Netflix 1 Ay — 2.30 AZN", callback_data="claim:Netflix Premium 1 Ay (2.30 AZN - 2.72 yox)")],
            [InlineKeyboardButton("▶️ YouTube Premium — 2.46 AZN", callback_data="claim:Youtube Premium (2.46 AZN - 2.96 yox)")],
            [InlineKeyboardButton("🎵 Spotify Premium — 2.30 AZN", callback_data="claim:Spotify Premium (2.30 AZN - 2.70 yox)")],
            [InlineKeyboardButton("🤖 Gemini Pro 18 Ay — 2.50 AZN", callback_data="claim:Gemini Pro 18 Ay (2.50 AZN - 3.00 yox)")],
            [InlineKeyboardButton("✂️ CapCut Pro 1 Ay — 3.00 AZN", callback_data="claim:Capcut Pro 1 Ay (3.00 AZN - 3.50 yox)")],
            [InlineKeyboardButton("⚡ CapCut 1600 Kredit — 3.80 AZN", callback_data="claim:Capcut Pro 1 Ay 1600 Kredit (3.80 AZN - 4.80 yox)")]
        ]
        await query.message.reply_text(
            "🎁 <b>İSTƏDİYİNİZ 1 ENDİRİMLİ HESABI SEÇİN (100 Xal):</b>\n━━━━━━━━━━━━━━━━━━━━",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(claim_buttons)
        )
        return

    # 6. Process Reward Claim
    if query.data.startswith("claim:"):
        chosen = query.data.split(":", 1)[1]
        ok, msg, vcode = claim_game_reward(user.id, user.username, user.first_name, chosen, "telegram_chat", "")
        if ok:
            succ_msg = (
                "🎉 <b>MÜKAFATINIZ TƏSDİQLƏNDİ!</b> 🏆\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🎁 <b>Seçdiyiniz Məhsul:</b> <b>{chosen}</b>\n"
                f"🎟️ <b>Xüsusi Kupon Kodunuz:</b> <code>{vcode}</code>\n\n"
                "📲 <b>Hesabı Təhvil Almaq Üçün:</b>\n"
                "Kupon kodunuzu WhatsApp vasitəsilə Adminə göndərin:\n"
                "👤 Admin: @Zeka233\n"
                f"📲 WhatsApp: https://wa.me/994773026579?text=Salam,%20Oyunda%20100%20xal%20toplayaraq%20{chosen}%20endirimi%20qazandim!%20Kupon:%20{vcode}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🌐 https://ucuzhesablar.com"
            )
            await query.message.edit_text(succ_msg, parse_mode='HTML')

            if ADMIN_CHAT_ID:
                baku_tz = datetime.timezone(datetime.timedelta(hours=4))
                now_str = datetime.datetime.now(baku_tz).strftime('%H:%M • %d.%m.%Y')
                uname_str = f"(@{user.username})" if user.username else "(istifadəçi adı yoxdur)"
                
                admin_alert = (
                    "🎮 <b>OYUN QALİBİ BİLDİRİŞİ (100 XAL)!</b> 🏆\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>Oyunçu:</b> {user.first_name} {uname_str}\n"
                    f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n"
                    f"🎁 <b>Seçdiyi Hesab:</b> <b>{chosen}</b>\n"
                    f"🎟️ <b>Kupon Kodu:</b> <code>{vcode}</code>\n"
                    f"🕒 <b>Vaxt:</b> {now_str}\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"💬 <a href=\"tg://user?id={user.id}\">İstifadəçiyə yaz</a>"
                )
                try:
                    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_alert, parse_mode='HTML')
                except Exception as e:
                    print(f"Admin alert err: {e}")
        else:
            await query.message.reply_text(f"⚠️ {msg}")
        return

    # 7. Game Leaderboard
    if query.data == "game_leaders":
        board = get_game_leaderboard(10)
        lines = ["🏆 <b>MƏHSUL OVÇUSU — ƏN ÇOX XAL TOPLAYANLAR:</b>\n━━━━━━━━━━━━━━━━━━━━"]
        medals = ["🥇", "🥈", "🥉", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
        for i, row in enumerate(board):
            uid, uname, fname, pts, tot = row
            display_name = fname or uname or f"İstifadəçi {uid}"
            lines.append(f"{medals[i]} <b>{display_name}</b> — <code>{tot} xal</code> <i>(balans: {pts})</i>")
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        await query.message.reply_text("\n".join(lines), parse_mode='HTML')
        return

async def check_prices_for_admin(app):
    """
    Background job: Runs at 09:00, 15:00, 19:00, 23:00 (Baku Time: UTC+4).
    Sends detailed report ONLY to Admin.
    """
    last_run_hour = None
    target_hours = {9, 15, 19, 23}

    while True:
        try:
            baku_tz = datetime.timezone(datetime.timedelta(hours=4))
            now = datetime.datetime.now(baku_tz)

            if now.hour in target_hours and now.hour != last_run_hour and now.minute <= 5:
                last_run_hour = now.hour
                print(f"⏰ [Baku Time {now.strftime('%H:%M')}] Admin üçün avtomatik qiymət yoxlanışı icra olunur...")

                report_lines = [
                    f"🔔 <b>[{now.strftime('%H:%M')}] 23 Mağaza Üzrə Rəqib Nəzarət Hesabatı</b>",
                    "━━━━━━━━━━━━━━━━━━━━",
                    "<i>(Yalnız Admin üçün gündəlik bazar analizi)</i>\n"
                ]

                for prod in TRACKED_PRODUCTS:
                    res = search_all_sites(prod)
                    if res['items']:
                        owner_b = res.get('owner_best')
                        cheapest = res['cheapest_item']

                        report_lines.append(f"📌 <b>{prod}:</b>")
                        if owner_b:
                            report_lines.append(f"   👑 <b>Bizdə:</b> <code>{owner_b['price']:.2f} AZN</code> ({owner_b['duration']} — aylıq {owner_b['monthly_price']:.2f} ₼)")
                        else:
                            report_lines.append("   👑 <b>Bizdə:</b> <i>Saytda tapılmadı</i>")

                        if res['is_owner_cheapest']:
                            comp_items = [it for it in res['items'] if not it.get('is_owner')]
                            if comp_items:
                                comp = comp_items[0]
                                report_lines.append(f"   🥇 Ən yaxın rəqib: <code>{comp['price']:.2f} AZN</code> ({comp['duration']} — {comp['site']})")
                                report_lines.append(f"   Status: ✅ <b>Bazarda ən sərfəlisi bizik!</b>")
                            else:
                                report_lines.append("   Status: ✅ <b>Rəqiblərdə yoxdur, tək bizik!</b>")
                        else:
                            report_lines.append(f"   ⚠️ <b>Diqqət:</b> <code>{cheapest['price']:.2f} AZN</code> ({cheapest['duration']} — {cheapest['site']})")
                            report_lines.append(f"   Status: 🔻 <i>Rəqibin aylıq mayası ({cheapest['monthly_price']:.2f} ₼) daha aşağıdır!</i>")
                        
                        report_lines.append("")

                report_lines.append("━━━━━━━━━━━━━━━━━━━━")
                report_lines.append("🌐 https://ucuzhesablar.com")

                if ADMIN_CHAT_ID:
                    await app.bot.send_message(
                        chat_id=ADMIN_CHAT_ID,
                        text="\n".join(report_lines),
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )
                    print("✅ Adminə avtomatik hesabat göndərildi!")

        except Exception as e:
            print(f"Xəta baş verdi (alert loop): {e}")

        await asyncio.sleep(45)

async def test_alert_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_CHAT_ID):
        await update.message.reply_text("⛔ Bu əmr yalnız Admin üçündür.")
        return

    wait_msg = await update.message.reply_text("⏳ <b>Admin Hesabatı hazırlanır...</b> 23 mağazada axtarış gedir...", parse_mode='HTML')
    
    baku_tz = datetime.timezone(datetime.timedelta(hours=4))
    now = datetime.datetime.now(baku_tz)

    report_lines = [
        f"🔔 <b>[{now.strftime('%H:%M')}] Canlı Rəqib Nəzarət Hesabatı (23 Mağaza)</b>",
        "━━━━━━━━━━━━━━━━━━━━",
        "<i>(Yalnız Admin üçün)</i>\n"
    ]

    for prod in TRACKED_PRODUCTS:
        res = search_all_sites(prod)
        if res['items']:
            owner_b = res.get('owner_best')
            cheapest = res['cheapest_item']

            report_lines.append(f"📌 <b>{prod}:</b>")
            if owner_b:
                report_lines.append(f"   👑 <b>Bizdə:</b> <code>{owner_b['price']:.2f} AZN</code> ({owner_b['duration']} — aylıq {owner_b['monthly_price']:.2f} ₼)")
            else:
                report_lines.append("   👑 <b>Bizdə:</b> <i>Saytda tapılmadı</i>")

            if res['is_owner_cheapest']:
                comp_items = [it for it in res['items'] if not it.get('is_owner')]
                if comp_items:
                    comp = comp_items[0]
                    report_lines.append(f"   🥇 Ən yaxın rəqib: <code>{comp['price']:.2f} AZN</code> ({comp['duration']} — {comp['site']})")
                    report_lines.append(f"   Status: ✅ <b>Bazarda ən sərfəlisi bizik!</b>")
                else:
                    report_lines.append("   Status: ✅ <b>Rəqiblərdə yoxdur, tək bizik!</b>")
            else:
                report_lines.append(f"   ⚠️ <b>Diqqət:</b> <code>{cheapest['price']:.2f} AZN</code> ({cheapest['duration']} — {cheapest['site']})")
                report_lines.append(f"   Status: 🔻 <i>Rəqibin aylıq mayası ({cheapest['monthly_price']:.2f} ₼) daha aşağıdır!</i>")
            
            report_lines.append("")

    report_lines.append("━━━━━━━━━━━━━━━━━━━━")
    report_lines.append("🌐 https://ucuzhesablar.com")

    await wait_msg.edit_text("\n".join(report_lines), parse_mode='HTML', disable_web_page_preview=True)

def run_bot(token: str):
    init_db()
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("website", website_cmd))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CommandHandler("stat", stat_cmd))
    app.add_handler(CommandHandler("statistika", stat_cmd))
    app.add_handler(CommandHandler("carx", wheel_cmd))
    app.add_handler(CommandHandler("wheel", wheel_cmd))
    app.add_handler(CommandHandler("oyun", game_cmd))
    app.add_handler(CommandHandler("game", game_cmd))
    app.add_handler(CommandHandler("xal", game_cmd))
    app.add_handler(CommandHandler("sual", quiz_cmd))
    app.add_handler(CommandHandler("quiz", quiz_cmd))
    app.add_handler(CommandHandler("qalibler", winners_cmd))
    app.add_handler(CommandHandler("kuponlar", game_rewards_cmd))
    app.add_handler(CommandHandler("alert_indi", test_alert_cmd))
    
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    async def post_init(application):
        asyncio.create_task(check_prices_for_admin(application))
    
    app.post_init = post_init
    print("Telegram bot started with 3D Game, 100 Logic Questions, 265-slot Wheel, and 23 sites...")
    app.run_polling()

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        run_bot(token)
    else:
        print("TELEGRAM_BOT_TOKEN tapılmadı.")
