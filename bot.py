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

def generate_ad_text(product_name, duration, price):
    return (
        f"🔥 <b>BAZARIN ƏN UCUZ QİYMƏTİ BİZDƏ!</b> 🔥\n\n"
        f"⚡ <b>Məhsul:</b> {product_name}\n"
        f"📅 <b>Müddət:</b> {duration}\n"
        f"💰 <b>QİYMƏT:</b> <code>{price:.2f} AZN</code>\n\n"
        f"✅ 100% Rəsmi və Zəmanətli çıxış\n"
        f"✅ Ani və avtomatik çatdırılma\n"
        f"🚀 Bütün rəqib saytlardan qat-qat sərfəli!\n\n"
        f"🌐 <b>Saytımızdan sifariş verin:</b> https://ucuzhesablar.com\n"
        f"📲 <b>WhatsApp ilə sifariş:</b> https://wa.me/994773026579"
    )

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)
    msg = (
        "👋 <b>Salam! Qiymət Radar Botuna xoş gəlmisiniz.</b>\n\n"
        "👑 <b>Ucuzhesablar.com</b> və digər 9 Azərbaycan rəqəmsal satış mağazasını "
        "eyni anda analiz edib <b>ən aşağı qiyməti</b> tapıram.\n\n"
        "🔍 <b>Axtarış üçün:</b>\n"
        "• Sadəcə məhsulun adını yazın (məs: <code>Capcut</code>, <code>Windows 11</code>)\n"
        "• Və ya <code>/search &lt;məhsul&gt;</code> əmrindən istifadə edin.\n\n"
        "💡 <i>Aşağıdakı hazır düymələrdən də dərhal seçə bilərsiniz:</i>"
    )
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>Botdan İstifadə Qaydaları:</b>\n\n"
        "1. <b>Axtarış:</b> <code>/search Capcut</code> və ya birbaşa məhsul adı yazın.\n"
        "2. <b>Məlumatlar:</b> Hər bir sayt üçün məhsulun dəqiq adı, müddəti (1 ay, 1 il, ömürlük) və qiyməti göstərilir.\n"
        "3. <b>Satış Mətni:</b> Axtarışdan sonra <b>«📝 Satış Mətnini Al»</b> düyməsinə basaraq WhatsApp və sosial şəbəkələr üçün hazır reklam mətni əldə edə bilərsiniz.\n"
        "4. <b>Admin Nəzarəti:</b> Hər gün saat <b>09:00, 15:00, 19:00, 23:00</b>-da rəqiblərin qiymət hesabatı yalnız Adminə göndərilir."
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
            "Məsələn: <code>/search Capcut Pro</code> və ya <code>/search Windows 11</code>",
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
        f"🔍 <b>«{query}»</b> üzrə 10 sayt analiz edilir...\n<i>Zəhmət olmasa gözləyin (1-3 saniyə)...</i>",
        parse_mode='HTML'
    )

    try:
        data = search_all_sites(query)
        if not data['items']:
            await wait_msg.edit_text(
                f"❌ <b>«{query}»</b> üzrə heç bir mağazada elan tapılmadı.\nZəhmət olmasa adı dəqiqləşdirib təkrar yazın.",
                parse_mode='HTML'
            )
            return

        lowest = data['lowest_price']
        cheapest_site = data['cheapest_site']
        is_owner_cheapest = data.get('is_owner_cheapest', False)

        lines = [
            f"🎯 <b>Məhsul Axtarışı:</b> <code>{query}</code>",
            "━━━━━━━━━━━━━━━━━━━━"
        ]

        if is_owner_cheapest:
            lines.append(f"👑 <b>ƏN UCUZ BİZDƏDİR (ucuzhesablar.com):</b> <code>{lowest:.2f} ₼</code> 🥇")
            lines.append("<i>(Təbriklər, bu məhsul üzrə bazarda lider sizsiniz!)</i>")
        else:
            lines.append(f"🏆 <b>Bazarın Ən Ucuz Qiyməti:</b> <code>{lowest:.2f} ₼</code> ({cheapest_site})")
            if data.get('owner_lowest'):
                diff = data['owner_lowest'] - lowest
                lines.append(f"ℹ️ Bizim saytda: <code>{data['owner_lowest']:.2f} ₼</code> (+{diff:.2f} ₼ fərq)")

        lines.append("━━━━━━━━━━━━━━━━━━━━\n📊 <b>Tapılan Elanlar (Müddət və Qiymət):</b>\n")

        # Select the best item for ad generator
        best_item = None
        for it in data['items']:
            if it.get('is_owner'):
                best_item = it
                break
        if not best_item:
            best_item = data['items'][0]

        for i, item in enumerate(data['items'][:8], 1):
            is_owner = item.get('is_owner', False)
            site_tag = "👑 <b>ucuzhesablar.com (Bizim Sayt)</b>" if is_owner else f"🏬 <b>{item['site']}</b>"
            
            lines.append(
                f"{i}. {site_tag}\n"
                f"   📌 <b>Elan:</b> {item['title']}\n"
                f"   📅 <b>Müddət:</b> <code>{item['duration']}</code>\n"
                f"   💵 <b>Qiymət:</b> <code>{item['price']:.2f} AZN</code>\n"
                f"   🔗 <a href=\"{item['url']}\">Elana bax →</a>\n"
            )

        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("⚡ <i>Ucuzhesablar.com Qiymət Radarı</i>")

        # Inline button to generate sales ad text
        duration_for_btn = best_item.get('duration', '1 Ay')
        price_for_btn = best_item.get('price', lowest)
        
        # Save search state in context or encode in callback data
        inline_buttons = [
            [InlineKeyboardButton("📝 Hazır Satış Mətnini Al", callback_data=f"ad:{query[:20]}:{duration_for_btn}:{price_for_btn}")],
            [InlineKeyboardButton("🌐 Ucuzhesablar.com-a Keçid", url="https://ucuzhesablar.com")]
        ]

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

    data = query.data
    if data.startswith("ad:"):
        parts = data.split(":")
        prod_name = parts[1]
        duration = parts[2]
        price = float(parts[3])

        ad_msg = generate_ad_text(prod_name, duration, price)
        reply = (
            "📋 <b>WhatsApp və Sosial Şəbəkələr Üçün Hazır Satış Mətni:</b>\n"
            "<i>(Aşağıdakı mətni kopyalayıb birbaşa paylaşa bilərsiniz)</i>\n\n"
            f"<code>{ad_msg}</code>"
        )
        await query.message.reply_text(reply, parse_mode='HTML', disable_web_page_preview=True)

async def check_prices_for_admin(app):
    """
    Background job: Checks prices at 09:00, 15:00, 19:00, 23:00 (Baku Time: UTC+4).
    Sends detailed report ONLY to Admin.
    """
    last_run_hour = None
    target_hours = {9, 15, 19, 23}

    while True:
        try:
            # Baku Time is UTC+4
            baku_tz = datetime.timezone(datetime.timedelta(hours=4))
            now = datetime.datetime.now(baku_tz)

            if now.hour in target_hours and now.hour != last_run_hour and now.minute <= 5:
                last_run_hour = now.hour
                print(f"⏰ [Baku Time {now.strftime('%H:%M')}] Admin üçün avtomatik qiymət yoxlanışı icra olunur...")

                report_lines = [
                    f"🔔 <b>[{now.strftime('%H:%M')}] Avtomatik Qiymət İzləmə Hesabatı</b>",
                    "━━━━━━━━━━━━━━━━━━━━",
                    "<i>(Yalnız Admin üçün göndərilən gündəlik rəqib analizi)</i>\n"
                ]

                for prod in TRACKED_PRODUCTS:
                    res = search_all_sites(prod)
                    if res['items']:
                        our_price = res.get('owner_lowest')
                        lowest = res['lowest_price']
                        cheapest_site = res['cheapest_site']

                        report_lines.append(f"📌 <b>{prod}:</b>")
                        if our_price:
                            report_lines.append(f"   👑 <b>Bizim qiymət:</b> <code>{our_price:.2f} AZN</code>")
                        else:
                            report_lines.append("   👑 <b>Bizim qiymət:</b> <i>Saytda tapılmadı</i>")

                        if res['is_owner_cheapest']:
                            # Find competitor lowest
                            competitor_items = [it for it in res['items'] if not it.get('is_owner')]
                            if competitor_items:
                                comp_lowest = competitor_items[0]['price']
                                diff = comp_lowest - our_price
                                report_lines.append(f"   🥇 Ən yaxın rəqib: <code>{comp_lowest:.2f} AZN</code> ({competitor_items[0]['site']})")
                                report_lines.append(f"   Status: ✅ <b>Liderik! ({diff:.2f} AZN daha ucuz)</b>")
                            else:
                                report_lines.append("   Status: ✅ <b>Rəqiblərdə yoxdur, tək bizik!</b>")
                        else:
                            diff = (our_price - lowest) if our_price else 0
                            report_lines.append(f"   ⚠️ <b>Diqqət:</b> <code>{lowest:.2f} AZN</code> ({cheapest_site})")
                            if our_price:
                                report_lines.append(f"   Status: 🔻 <i>Rəqib bizdən {diff:.2f} AZN daha ucuz satır!</i>")
                        
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

        # Sleep for 45 seconds before checking time again
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
        f"🔔 <b>[{now.strftime('%H:%M')}] Canlı Qiymət Nəzarət Hesabatı</b>",
        "━━━━━━━━━━━━━━━━━━━━",
        "<i>(Yalnız Admin üçün)</i>\n"
    ]

    for prod in TRACKED_PRODUCTS:
        res = search_all_sites(prod)
        if res['items']:
            our_price = res.get('owner_lowest')
            lowest = res['lowest_price']
            cheapest_site = res['cheapest_site']

            report_lines.append(f"📌 <b>{prod}:</b>")
            if our_price:
                report_lines.append(f"   👑 <b>Bizim qiymət:</b> <code>{our_price:.2f} AZN</code>")
            else:
                report_lines.append("   👑 <b>Bizim qiymət:</b> <i>Saytda tapılmadı</i>")

            if res['is_owner_cheapest']:
                competitor_items = [it for it in res['items'] if not it.get('is_owner')]
                if competitor_items:
                    comp_lowest = competitor_items[0]['price']
                    diff = comp_lowest - our_price
                    report_lines.append(f"   🥇 Ən yaxın rəqib: <code>{comp_lowest:.2f} AZN</code> ({competitor_items[0]['site']})")
                    report_lines.append(f"   Status: ✅ <b>Liderik! ({diff:.2f} AZN daha ucuz)</b>")
                else:
                    report_lines.append("   Status: ✅ <b>Rəqiblərdə yoxdur, tək bizik!</b>")
            else:
                diff = (our_price - lowest) if our_price else 0
                report_lines.append(f"   ⚠️ <b>Diqqət:</b> <code>{lowest:.2f} AZN</code> ({cheapest_site})")
                if our_price:
                    report_lines.append(f"   Status: 🔻 <i>Rəqib bizdən {diff:.2f} AZN daha ucuz satır!</i>")
            
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
    
    # Schedule background alert task on bot startup
    async def post_init(application):
        asyncio.create_task(check_prices_for_admin(application))
    
    app.post_init = post_init
    print("Telegram bot started with 4 scheduled alert hours (09:00, 15:00, 19:00, 23:00)...")
    app.run_polling()

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        run_bot(token)
    else:
        print("TELEGRAM_BOT_TOKEN tapılmadı.")
