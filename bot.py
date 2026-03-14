import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- CONFIGURATION (Directly Integrated) ---
TELEGRAM_BOT_TOKEN = '8777695184:AAGfN_J5eF62UPozlDEQqbLk80X8YOb9dEE'
RAPID_API_KEY = 'bad107bfffmsh8d49bf7c3269161p1e812cjsn995c7823fad1'
RAPID_API_HOST = 'download-all-in-one-elite.p.rapidapi.com'
API_URL = "https://download-all-in-one-elite.p.rapidapi.com/v1/social/autolink"

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"👋 *Hi {user_name}!* \n\n"
        "Main ek *All-in-One Video Downloader* bot hoon.\n"
        "Main in platforms ko support karta hoon:\n"
        "• Instagram Reels/IGTV\n"
        "• TikTok (No Watermark)\n"
        "• YouTube & Facebook\n\n"
        "📥 *Bas link bhejein aur magic dekhein!*"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # URL Validation
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ Bhai, ye valid link nahi hai. Please proper URL bhejein.")
        return

    status_msg = await update.message.reply_text("⚡ *Processing...* Server se connect kar raha hoon.", parse_mode="Markdown")

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPID_API_HOST,
        "x-rapidapi-key": RAPID_API_KEY
    }
    payload = {"url": url}

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            response = await client.post(API_URL, json=payload, headers=headers)
            
            if response.status_code != 200:
                await status_msg.edit_text("❌ API Error: Shayad link support nahi hai ya limit khatam ho gayi.")
                return

            data = response.json()
            medias = data.get("medias", [])
            title = data.get("title", "Video File")

            # Finding the best MP4 video link
            video_url = None
            for item in medias:
                if item.get("extension") == "mp4" or item.get("type") == "video":
                    video_url = item.get("url")
                    break

            if video_url:
                await status_msg.edit_text("📤 *Video mil gayi!* Ab upload kar raha hoon...")
                try:
                    # Telegram supports sending via URL (Max 50MB)
                    await update.message.reply_video(
                        video=video_url,
                        caption=f"✅ *{title}*\n\nDownloaded via @allinonevideodown_bot",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    # If video is too large, send direct link
                    await update.message.reply_text(
                        f"⚠️ *File size badi hai!* \n\nDirect yahan se download karein:\n🔗 [Download Link]({video_url})",
                        parse_mode="Markdown"
                    )
            else:
                await status_msg.edit_text("❌ Sorry! Is link se koi download-able video nahi mili.")

        except Exception as e:
            logging.error(f"Error: {e}")
            await status_msg.edit_text("❌ Server busy hai ya koi technical issue hai. Thodi der baad try karein.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot chalu ho gaya hai...")
    application.run_polling()