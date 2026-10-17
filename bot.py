import os
import re
import asyncio
import datetime
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from scraper import search_all_sites
from database import init_db, log_user_activity, get_statistics

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8495554960")

USER_KEYBOARD = [
    ["🎬 Capcut Pro", "🪟 Windows 11 Pro"],
    ["🎨 Canva Pro", "💼 Microsoft 365"],
    ["🎵 Spotify", "🍿 Netflix 4K"],
    ["👑 Ucuzhesablar.com", "❓ Kömək"]
]

ADMIN_KEYBOARD = [
    ["🎬 Capcut Pro", "🪟 Windows 11 Pro"],
    ["🎨 Canva Pro", "💼 Microsoft 365"],
    ["🎵 Spotify", "🍿 Netflix 4K"],
    ["📊 Statistika Paneli", "👑 Ucuzhesablar.com"]
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
        "(based, prom, elnur, itemhesab, lisenziya, digibaku, igame, strokt, wepay, smartelan və s.) "
        "eyni anda analiz edib <b>ən sərfəli qiyməti</b> tapıram.\n\n"
        "🔍 <b>Axtarış üçün:</b>\n"
        "• Sadəcə məhsulun adını yazın (məs: <code>Capcut</code>, <code>Spotify</code>, <code>Canva</code>)\n"
        "• Və ya <code>/search &lt;məhsul&gt;</code> əmrindən istifadə edin.\n\n"
        "💡 <i>Aşağıdakı hazır düymələrdən də dərhal seçə bilərsiniz:</i>"
    )
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username, user.first_name)
    text = (
        "ℹ️ <b>Botdan İstifadə Qaydaları:</b>\n\n"
        "1. <b>23 Saytda Axtarış:</b> <code>/search Canva Pro</code> və ya birbaşa məhsul adını yazın. Bot bütün 23 mağazada anında axtarış aparır.\n"
        "2. <b>Ağıllı Aylıq Müqayisə:</b> Tək məbləğə görə deyil, aylıq maya dəyərinə görə ən sərfəli təklif önə çıxarılır.\n"
        "3. <b>Birbaşa Keçid:</b> Nəticənin altındakı düymə sizi birbaşa həmin məhsulun Ucuzhesablar.com-dakı səhifəsinə aparır."
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
    user = update.effective_user
    
    if raw_text == "❓ Kömək":
        await help_cmd(update, context)
        return
    elif raw_text == "👑 Ucuzhesablar.com":
        await website_cmd(update, context)
        return
    elif raw_text == "📊 Statistika Paneli":
        await stat_cmd(update, context)
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

    user_id = str(update.effective_user.id)

    # Refresh statistics callback
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

    # Ad text callback (Admin only)
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
    app.add_handler(CommandHandler("alert_indi", test_alert_cmd))
    
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    async def post_init(application):
        asyncio.create_task(check_prices_for_admin(application))
    
    app.post_init = post_init
    print("Telegram bot started with 23 sites and Admin Statistics panel...")
    app.run_polling()

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        run_bot(token)
    else:
        print("TELEGRAM_BOT_TOKEN tapılmadı.")
