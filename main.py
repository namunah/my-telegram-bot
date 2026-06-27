import os
import time
from threading import Thread
from flask import Flask
import telebot
from google import genai

# =======================================================
# ⚙️ CREDENTIAL MAPPING
# =======================================================
TELEGRAM_TOKEN = "8806241210:AAFrbsT-KutdnLqNXdK5PlSIuaKVYiYAv1I"
GEMINI_API_KEY = "AQ.Ab8RN6JeiFps-3UyK8-ifhHMjIkSqAr9gz3YMeDGm8RRBSjmqw"

# 1. Initialize modern GenAI Client & Bot
client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 2. Setup Flask Web Server
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot status: Operational & Connected to Gemini Cloud Engine."

def run_web_server():
    # Render automatically provides a 'PORT' environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. Core Message Processing Pipeline
@bot.message_handler(func=lambda message: True)
def process_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=message.text.strip()
        )
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "🤖 Handled query, but no text was returned.")
    except Exception as e:
        print(f"⚠️ API Error: {str(e)}")
        bot.reply_to(message, "⚠️ System encountered an issue processing that query.")

# 4. Main Operational Launcher
if __name__ == "__main__":
    # Clean up old webhooks
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    
    # Start the web server thread so Render stays happy
    print("🌐 Starting background web layout...")
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Start listening to Telegram
    print("⚡ Bot pipeline is actively running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
