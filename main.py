import os
import telebot
from openai import OpenAI
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')
OWNER_HANDLE = "@usergotcigs"
BOT_NAME = "Mikasa"

# Initialize Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize OpenAI Client (Hugging Face Router)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# Flask app to keep Render happy
app = Flask(__name__)

@app.route('/')
def home():
    return "Mikasa Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- BOT LOGIC ---

SYSTEM_PROMPT = f"""
You are {BOT_NAME}, a human-like, friendly, and cool AI companion. 
Your owner is {OWNER_HANDLE}. 
You speak in a mix of Hindi, Hinglish, and English naturally, just like a modern Indian friend.
Keep your replies concise, engaging, and helpful. 
Avoid sounding like a robotic assistant. Use emojis occasionally.
"""

def get_ai_response(user_text):
    try:
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1:novita",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            max_tokens=500
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling AI: {e}")
        return "Arre yaar, thoda network issue hai. Can you try again? 😅"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        f"Hi! I am {BOT_NAME}. ✨\n"
        f"Main English, Hindi aur Hinglish samajhti hoon.\n"
        f"Created by {OWNER_HANDLE}. Bolna, kya haal chaal?"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Show "typing..." action in Telegram
    bot.send_chat_action(message.chat.id, 'typing')
    
    user_query = message.text
    response = get_ai_response(user_query)
    
    bot.reply_to(message, response)

# --- EXECUTION ---
if __name__ == "__main__":
    # Start Flask in a separate thread
    t = Thread(target=run_flask)
    t.start()
    
    print(f"{BOT_NAME} is now active...")
    # Start Telegram Polling
    bot.infinity_polling()
