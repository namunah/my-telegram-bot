import os
import time
from threading import Thread
from flask import Flask
import telebot
from google import genai
from google.genai.errors import APIError

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
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. Core Message Processing Pipeline with Traffic Fallbacks
@bot.message_handler(func=lambda message: True)
def process_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    user_prompt = message.text.strip()
    
    # List of models to try in sequence if one hits a 503 error
    fallback_models = ['gemini-2.5-flash', 'gemini-1.5-flash']
    response_text = None

    for model_name in fallback_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt
            )
            if response.text:
                response_text = response.text
                break  # Successfully got an answer, break out of loop
        except APIError as api_err:
            print(f"🔄 Model {model_name} busy or unavailable. Error: {api_err}")
            time.sleep(1)  # Brief pause before fallback attempt
            continue
        except Exception as e:
            print(f"⚠️ Unexpected error on {model_name}: {e}")
            continue

    # Dispatch final response back to Telegram
    if response_text:
        bot.reply_to(message, response_text)
    else:
        bot.reply_to(message, "⚠️ All Gemini cloud engines are currently facing extreme traffic spikes. Please wait a minute and try again.")

# 4. Main Operational Launcher
if __name__ == "__main__":
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    
    print("🌐 Starting background web layout...")
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("⚡ Bot pipeline is actively running with fallback engines...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
