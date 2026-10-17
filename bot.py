import os
import re
import asyncio
import datetime
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from scraper import search_all_sites
from database import (
    init_db, log_user_activity, get_statistics,
    check_user_wheel_status, spin_wheel, get_wheel_stock_info, get_wheel_winners
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8495554960")

USER_KEYBOARD = [
    ["🎬 Capcut Pro", "🪟 Windows 11 Pro"],
    ["🎨 Canva Pro", "💼 Microsoft 365"],
    ["🎵 Spotify", "🍿 Netflix 4K"],
    ["🎡 Çarxıfələk (Hədiyyə)", "👑 Ucuzhesablar.com"],
    ["❓ Kömək"]
]

ADMIN_KEYBOARD = [
    ["🎬 Capcut Pro", "🪟 Windows 11 Pro"],
    ["🎨 Canva Pro", "💼 Microsoft 365"],
    ["🎵 Spotify", "🍿 Netflix 4K"],
    ["🎡 Çarxıfələk", "📊 Statistika Paneli"],
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
    baku_tz = datetime.timezone(datetime.timedelta(hours=4))
    now = datetime.datetime.now(baku_tz).strftime('%H:%M:%S • %d.%m.%Y')

    # Wheel info
    stock_info = get_wheel_stock_info()
    winners = get_wheel_winners()
    
    stock_text = ""
    for name, total, rem in stock_info:
        stock_text += f"   • {name}: <code>{rem}/{total} ədəd qalıb</code>\n"

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
        "📊 <b>QIYMƏT RADAR — STATİSTİKA PANELİ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Toplam İstifadəçi:</b> <code>{stats['total_users']} nəfər</code>\n"
        f"🟢 <b>Hal-hazırda Aktiv (Online):</b> <code>{stats['online_users']} nəfər</code> <i>(son 15 dəqiqə)</i>\n"
        f"⚡ <b>Son 24 saatda Aktiv:</b> <code>{stats['active_24h']} nəfər</code>\n"
        f"🔍 <b>Toplam Axtarış Sayı:</b> <code>{stats['total_searches']} dəfə</code>\n\n"
        "🎡 <b>Çarxıfələk Vəziyyəti:</b>\n"
        f"   🏆 Qalib sayı: <code>{len(winners)} nəfər</code>\n"
        f"{stock_text}\n"
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
        "🎡 <b>Xüsusi Kampaniya:</b> «🎡 Çarxıfələk» bölməsinə daxil olaraq şansınızı yoxlaya və pulsuz premium hədiyyələr qazana bilərsiniz!\n\n"
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
        "1. <b>23 Saytda Axtarış:</b> <code>/search Canva Pro</code> və ya birbaşa məhsul adını yazın. Bot bütün 23 mağazada anında axtarış aparır.\n"
        "2. <b>Ağıllı Aylıq Müqayisə:</b> Tək məbləğə görə deyil, aylıq maya dəyərinə görə ən sərfəli təklif önə çıxarılır.\n"
        "3. <b>🎡 Çarxıfələk:</b> Hər istifadəçi yalnız 1 dəfə çarxı çevirərək Gemini Pro 18 ay, Microsoft 365 və ya Canva Pro qazana bilər!\n"
        "4. <b>Birbaşa Keçid:</b> Nəticənin altındakı düymə sizi birbaşa həmin məhsulun Ucuzhesablar.com-dakı səhifəsinə aparır."
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

    has_spun, prize, spin_time = check_user_wheel_status(user.id)
    if has_spun:
        if prize:
            msg = (
                f"⛔ <b>Siz artıq çarxı çevirmisiniz!</b>\n\n"
                f"🎉 Qazandığınız hədiyyə: <b>{prize}</b> 🎁\n\n"
                f"✅ Hədiyyənizi təhvil almaq üçün Adminlə əlaqə saxlayın:\n"
                f"👤 Admin: @Zeka233\n"
                f"📲 WhatsApp: https://wa.me/994773026579\n"
                f"🆔 Sizin ID: <code>{user.id}</code>"
            )
        else:
            msg = (
                "⛔ <b>Siz artıq çarxı çevirmisiniz!</b>\n\n"
                "😢 Təəssüf ki, bəxtiniz gətirməmişdi. Hər istifadəçinin sistemdə <b>yalnız 1 dəfə</b> şansı var.\n\n"
                "🛍️ Ən ucuz qiymətlərlə alış-veriş üçün saytımıza daxil olun:\n"
                "🌐 https://ucuzhesablar.com"
            )
        await update.message.reply_text(msg, parse_mode='HTML')
        return

    # User has not spun yet - present the wheel
    stock_info = get_wheel_stock_info()
    stock_lines = ""
    for name, total, rem in stock_info:
        stock_lines += f"• 🎁 <b>{name}</b> — <i>{rem} ədəd qalıb</i>\n"

    msg = (
        "🎡 <b>UCUZHESABLAR.COM — BÖYÜK ÇARXIFƏLƏK!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Şansınızı yoxlayın və tamamilə <b>PULSUZ</b> premium hədiyyələrdən birini qazanın!\n\n"
        "🏆 <b>Mövcud Hədiyyələr (Toplam 5 Ədəd):</b>\n"
        f"{stock_lines}\n"
        "🎯 <b>Şərtlər:</b>\n"
        "• Çarxın <b>30 xanası (gözü)</b> var.\n"
        "• Hər istifadəçinin <b>yalnız 1 dəfə</b> çevirmək haqqı var (Telegram ID ilə qeydə alınır).\n\n"
        "👇 <i>Şansınızı yoxlamaq üçün aşağıdakı düyməyə basın:</i>"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 Çarxı Fırlat (1 Şans)!", callback_data="spin_wheel")]
    ])
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=kb)

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
    for i, (uid, uname, fname, prize, dt) in enumerate(winners, 1):
        uname_str = f"(@{uname})" if uname else ""
        lines.append(
            f"{i}. <b>{fname}</b> {uname_str}\n"
            f"   🎁 Hədiyyə: <b>{prize}</b>\n"
            f"   🆔 ID: <code>{uid}</code>\n"
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
    elif "çarxıfələk" in raw_text.lower() or "carx" in raw_text.lower():
        await wheel_cmd(update, context)
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

        # "Hazır Satış Mətni" button ONLY FOR ADMIN!
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

    # 1. Refresh statistics callback (Admin only)
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

    # 2. Ad text callback (Admin only)
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

    # 3. Spin Wheel callback
    if query.data == "spin_wheel":
        # Check if already spun
        has_spun, prev_prize, _ = check_user_wheel_status(user.id)
        if has_spun:
            await query.message.reply_text(
                "⛔ <b>Siz artıq çarxı çevirmisiniz!</b> Hər istifadəçinin yalnız 1 şansı var.",
                parse_mode='HTML'
            )
            return

        # Spinning animation
        await query.message.edit_text(
            "🎰 <b>Çarx fırlanır...</b> 🎡\n\n"
            "<code>[ ░░░░░░░░░░ ] 25%</code>\n"
            "<i>Bəxtiniz yoxlanılır...</i>",
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

        # Execute spin in database
        status, prize_won = spin_wheel(user.id, user.username, user.first_name)

        if status == "WIN" and prize_won:
            # Winner message to user
            win_msg = (
                f"🎉 <b>TƏBRİKLƏR! SİZ QALİB OLDUNUZ!</b> 🎁\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🏆 Qazandığınız Hədiyyə: <b>{prize_won}</b>!\n\n"
                f"✅ Hədiyyənizi aktivləşdirmək və təhvil almaq üçün birbaşa Adminlə əlaqə saxlayın:\n"
                f"👤 <b>Admin:</b> @Zeka233\n"
                f"📲 <b>WhatsApp:</b> https://wa.me/994773026579\n"
                f"🆔 <b>Sizin Telegram ID:</b> <code>{user.id}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 https://ucuzhesablar.com"
            )
            await query.message.edit_text(win_msg, parse_mode='HTML')

            # SEND NOTIFICATION IMMEDIATELY TO ADMIN!
            if ADMIN_CHAT_ID:
                baku_tz = datetime.timezone(datetime.timedelta(hours=4))
                now_str = datetime.datetime.now(baku_tz).strftime('%H:%M • %d.%m.%Y')
                uname_str = f"(@{user.username})" if user.username else "(istifadəçi adı yoxdur)"
                
                admin_alert = (
                    "🚨 <b>YENİ ÇARXIFƏLƏK QALİBİ VAR!</b> 🎁\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>Qalib:</b> {user.first_name} {uname_str}\n"
                    f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n"
                    f"🎁 <b>Qazandığı Hədiyyə:</b> <b>{prize_won}</b>\n"
                    f"🕒 <b>Vaxt:</b> {now_str}\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"💬 <b>İstifadəçiyə yaz:</b> <a href=\"tg://user?id={user.id}\">Telegram Çatı Aç</a>"
                )
                try:
                    await context.bot.send_message(
                        chat_id=ADMIN_CHAT_ID,
                        text=admin_alert,
                        parse_mode='HTML'
                    )
                except Exception as e:
                    print(f"Admin bildiriş xətası: {e}")

        elif status == "LOSE":
            lose_msg = (
                "😢 <b>Təəssüf ki, bu dəfə bəxtiniz gətirmədi!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "Çarx boş xanada dayandı. Hər istifadəçi üçün yalnız 1 dəfə çevirmək limiti var.\n\n"
                "🛍️ <i>Amma ən ucuz qiymətlərlə premium hesabları və proqramları saytımızdan dərhal əldə edə bilərsiniz:</i>\n"
                "🌐 <b>Saytımız:</b> https://ucuzhesablar.com\n"
                "📲 <b>WhatsApp:</b> https://wa.me/994773026579"
            )
            await query.message.edit_text(lose_msg, parse_mode='HTML')
        else:
            await query.message.edit_text(
                "⛔ <b>Siz artıq çarxı çevirmisiniz!</b> Hər istifadəçinin yalnız 1 şansı var.",
                parse_mode='HTML'
            )

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
    app.add_handler(CommandHandler("qalibler", winners_cmd))
    app.add_handler(CommandHandler("alert_indi", test_alert_cmd))
    
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    async def post_init(application):
        asyncio.create_task(check_prices_for_admin(application))
    
    app.post_init = post_init
    print("Telegram bot started with Wheel of Fortune, 23 sites, and Admin statistics...")
    app.run_polling()

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        run_bot(token)
    else:
        print("TELEGRAM_BOT_TOKEN tapılmadı.")
