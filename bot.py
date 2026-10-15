import os
import re
import asyncio
import datetime
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from scraper import search_all_sites

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8495554960")

KEYBOARD = [
    ["🎬 Capcut Pro", "🪟 Windows 11 Pro"],
    ["🎨 Canva Pro", "💼 Microsoft 365"],
    ["🎵 Spotify", "🍿 Netflix 4K"],
    ["👑 Ucuzhesablar.com", "❓ Kömək"]
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
        f"🚀 Bütün digər mağazalardan daha sərfəli!\n\n"
        f"🌐 <b>Saytımızdan birbaşa sifariş:</b> https://ucuzhesablar.com\n"
        f"📲 <b>WhatsApp ilə sifariş:</b> https://wa.me/994773026579"
    )

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)
    msg = (
        "👋 <b>Salam! Qiymət Radar Botuna xoş gəlmisiniz.</b>\n\n"
        "👑 <b>Ucuzhesablar.com</b> və digər 9 Azərbaycan rəqəmsal satış mağazasını "
        "eyni anda analiz edib <b>aylıq və ümumi ən sərfəli qiyməti</b> tapıram.\n\n"
        "🔍 <b>Axtarış üçün:</b>\n"
        "• Sadəcə məhsulun adını yazın (məs: <code>Capcut</code>, <code>Spotify</code>, <code>Canva</code>)\n"
        "• Və ya <code>/search &lt;məhsul&gt;</code> əmrindən istifadə edin.\n\n"
        "💡 <i>Aşağıdakı hazır düymələrdən də dərhal seçə bilərsiniz:</i>"
    )
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>Botdan İstifadə Qaydaları:</b>\n\n"
        "1. <b>Dəqiq Axtarış:</b> <code>/search Canva Pro</code> və ya birbaşa məhsul adını yazın. Bot yalnız axtarılan məhsulu tapır və digər proqramlarla qarışdırmır.\n"
        "2. <b>Ədalətli Qiymət Analizi:</b> Bot tək məbləğə baxmır, ayların fərqini də hesablayır (Məsələn: 4 ay 6.20 ₼ verən təklif, 1 ay 4.99 ₼ verəndən daha sərfəli çıxır, çünki aylıq cəmi 1.55 ₼ edir!).\n"
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

    # Clean emojis (e.g. "🎬 Capcut Pro" -> "Capcut Pro")
    clean_query = re.sub(r'[^\w\s\+\-\.]', '', raw_text).strip()
    if not clean_query:
        clean_query = raw_text

    await execute_search(update, clean_query)

async def execute_search(update: Update, query: str):
    wait_msg = await update.message.reply_text(
        f"🔍 <b>«{query}»</b> üzrə 10 mağazada dəqiq axtarış edilir...\n<i>Zəhmət olmasa gözləyin (1-3 saniyə)...</i>",
        parse_mode='HTML'
    )

    try:
        data = search_all_sites(query)
        if not data['items']:
            await wait_msg.edit_text(
                f"❌ <b>«{query}»</b> üzrə mağazalarda dəqiq uyğun gələn elan tapılmadı.\nZəhmət olmasa adı dəqiqləşdirib təkrar yazın.",
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

        # Smart banner explaining who is truly cheaper taking duration into account
        if is_owner_cheapest and owner_best:
            lines.append(f"👑 <b>ƏN SƏRFƏLİ BİZDƏDİR (ucuzhesablar.com)!</b> 🥇")
            if owner_best['duration'] != "1 Ay":
                lines.append(f"💡 Bizdə <b>{owner_best['duration']}</b> cəmi <code>{owner_best['price']:.2f} AZN</code> (Aylıq: <b>{owner_best['monthly_price']:.2f} ₼</b>)!")
                # show competitor comparison
                comp_items = [it for it in data['items'] if not it.get('is_owner')]
                if comp_items:
                    comp = comp_items[0]
                    lines.append(f"<i>(Rəqibdə {comp['site']}: {comp['duration']} üçün {comp['price']:.2f} ₼, yəni aylıq {comp['monthly_price']:.2f} ₼!)</i>")
            else:
                lines.append(f"💰 Bizim qiymət: <code>{owner_best['price']:.2f} AZN</code> ({owner_best['duration']})")
        else:
            lines.append(f"🏆 <b>Ən Sərfəli Təklif:</b> <code>{cheapest_item['price']:.2f} AZN</code> ({cheapest_item['duration']} — {cheapest_item['site']})")
            lines.append(f"📊 Aylıq maya dəyəri: <b>{cheapest_item['monthly_price']:.2f} AZN/ay</b>")
            if owner_best:
                lines.append(f"👑 Bizim qiymət: <code>{owner_best['price']:.2f} AZN</code> ({owner_best['duration']} — aylıq {owner_best['monthly_price']:.2f} ₼)")

        lines.append("━━━━━━━━━━━━━━━━━━━━\n📊 <b>Tapılan Dəqiq Elanlar (Aylıq Sərfəlilik Sırası ilə):</b>\n")

        for i, item in enumerate(data['items'][:8], 1):
            is_owner = item.get('is_owner', False)
            site_tag = "👑 <b>ucuzhesablar.com (Bizim Sayt)</b>" if is_owner else f"🏬 <b>{item['site']}</b>"
            top_badge = " 🥇 (Ən Sərfəli)" if i == 1 else ""

            # Show unit price per month if duration is more than 1 month
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
        lines.append("⚡ <i>Ucuzhesablar.com • Real Qiymət Analizi</i>")

        # Buttons logic:
        # 1. Direct link to THAT SPECIFIC PRODUCT on ucuzhesablar.com!
        inline_buttons = [
            [InlineKeyboardButton("🛍️ Məhsulu Sifariş Et (Ucuzhesablar.com)", url=owner_url)]
        ]

        # 2. "Hazır Satış Mətni" button ONLY FOR ADMIN!
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

    # Double check admin permission
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_CHAT_ID):
        await query.message.reply_text("⛔ Bu funksiya yalnız Admin üçündür.")
        return

    data = query.data
    if data.startswith("ad:"):
        parts = data.split(":")
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
                    f"🔔 <b>[{now.strftime('%H:%M')}] Avtomatik Rəqib Nəzarət Hesabatı</b>",
                    "━━━━━━━━━━━━━━━━━━━━",
                    "<i>(Yalnız Admin üçün göndərilən gündəlik qiymət analizi)</i>\n"
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
    """Admin-only manual trigger for the price check report."""
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_CHAT_ID):
        await update.message.reply_text("⛔ Bu əmr yalnız Admin üçündür.")
        return

    wait_msg = await update.message.reply_text("⏳ <b>Admin Hesabatı hazırlanır...</b> Bütün məhsullar yoxlanılır...", parse_mode='HTML')
    
    baku_tz = datetime.timezone(datetime.timedelta(hours=4))
    now = datetime.datetime.now(baku_tz)

    report_lines = [
        f"🔔 <b>[{now.strftime('%H:%M')}] Canlı Rəqib Nəzarət Hesabatı</b>",
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
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("website", website_cmd))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CommandHandler("alert_indi", test_alert_cmd))
    
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    async def post_init(application):
        asyncio.create_task(check_prices_for_admin(application))
    
    app.post_init = post_init
    print("Telegram bot started with upgraded logic and admin-only features...")
    app.run_polling()

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        run_bot(token)
    else:
        print("TELEGRAM_BOT_TOKEN tapılmadı.")
