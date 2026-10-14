import os
import re
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from scraper import search_all_sites

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

KEYBOARD = [
    ["🎬 Capcut Pro", "🪟 Windows 11 Pro"],
    ["🎨 Canva Pro", "💼 Office 365"],
    ["🎵 Spotify", "🤖 ChatGPT Plus"],
    ["❓ Necə işləyir?"]
]

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)
    msg = (
        "👋 <b>Salam! Mən Qiymət Radar Botuyam.</b>\n\n"
        "Sizin üçün 9 Azərbaycan rəqəmsal satış mağazasını "
        "(based.az, prom.az, elnur.store, itemhesab, dolphgame və s.) "
        "eyni anda yoxlayıb <b>ən aşağı qiyməti</b> tapıram.\n\n"
        "💡 <i>Sadəcə axtarmaq istədiyiniz məhsulun adını yazın və ya aşağıdakı düymələrdən seçin:</i>"
    )
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=reply_markup)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>Necə işləyir?</b>\n\n"
        "1. İstədiyiniz məhsulun adını yazırsınız (Məs: <code>Capcut</code> və ya <code>Windows 11</code>).\n"
        "2. Bot 9 saytda eyni anda axtarış edir.\n"
        "3. Ən ucuz rəqibi və bazarda ən ucuz satmağınız üçün <b>Tövsiyə Satış Qiyməti</b>ni çıxarır.\n\n"
        "🌐 Mobil panel üçün brauzerdən də daxil ola bilərsiniz."
    )
    await update.message.reply_text(text, parse_mode='HTML')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text.strip()
    
    if raw_text == "❓ Necə işləyir?":
        await help_cmd(update, context)
        return

    # Clean emojis from shortcuts (e.g. "🎬 Capcut Pro" -> "Capcut Pro")
    clean_query = re.sub(r'[^\w\s\+\-\.]', '', raw_text).strip()
    if not clean_query:
        clean_query = raw_text

    wait_msg = await update.message.reply_text(
        f"🔍 <b>«{clean_query}»</b> üzrə 9 sayt yoxlanılır...\n<i>Zəhmət olmasa gözləyin (1-3 saniyə)...</i>",
        parse_mode='HTML'
    )

    try:
        data = search_all_sites(clean_query)
        
        if not data['items']:
            await wait_msg.edit_text(
                f"❌ <b>«{clean_query}»</b> üzrə heç bir nəticə tapılmadı.\nZəhmət olmasa adı dəqiqləşdirib təkrar yazın.",
                parse_mode='HTML'
            )
            return

        lowest = data['lowest_price']
        cheapest_site = data['cheapest_site']
        rec_price = data['recommended_price']

        lines = [
            f"🎯 <b>Məhsul:</b> <code>{clean_query}</code>",
            "━━━━━━━━━━━━━━━━━━━━",
            f"🏆 <b>Bazarın Ən Ucuz Qiyməti:</b> <code>{lowest:.2f} ₼</code> ({cheapest_site})",
            f"💡 <b>Sənin Satış Qiymətin:</b> <code>{rec_price:.2f} ₼</code>",
            "<i>(Bütün rəqiblərdən daha ucuz olmaq üçün)</i>",
            "━━━━━━━━━━━━━━━━━━━━",
            f"📊 <b>Saytlar Üzrə Qiymətlər ({data['total_found']} təklif):</b>\n"
        ]

        inline_buttons = []
        for i, item in enumerate(data['items'][:8], 1):
            is_top = (i == 1)
            badge = " 🥇 (Ən Ucuz)" if is_top else ""
            lines.append(f"<b>{i}. {item['site']}</b> — <code>{item['price']:.2f} ₼</code>{badge}\n   └ <i>{item['title'][:40]}</i>")
            
            # Add top 3 links as inline buttons
            if i <= 3 and item.get('url'):
                inline_buttons.append([InlineKeyboardButton(f"🔗 {item['site']} ({item['price']:.2f} ₼)", url=item['url'])])

        lines.append("\n━━━━━━━━━━━━━━━━━━━━")
        lines.append("⚡ <i>Qiymət Radar • 7/24 Avtomatik Sistem</i>")

        reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None
        await wait_msg.edit_text("\n".join(lines), parse_mode='HTML', reply_markup=reply_markup, disable_web_page_preview=True)

    except Exception as e:
        await wait_msg.edit_text(f"⚠️ Xəta baş verdi: {str(e)}")

def run_bot(token: str):
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Telegram bot started...")
    app.run_polling()

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        run_bot(token)
    else:
        print("TELEGRAM_BOT_TOKEN tapılmadı. .env faylına və ya mühit dəyişənlərinə əlavə edin.")
