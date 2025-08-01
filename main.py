import telebot
import os
import datetime
import random
import requests
from dotenv import load_dotenv

load_dotenv()  # تحميل المتغيرات من ملف .env

BOT_TOKEN = os.getenv('BOT_TOKEN') or "ضع_توكن_هنا"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or ""

bot = telebot.TeleBot(BOT_TOKEN)

def save_user(user):
    with open("users.txt", "a", encoding="utf-8") as f:
        f.write(f"{user.id} - {user.first_name}\n")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.from_user)
    bot.reply_to(message, "مرحباً! البوت يعمل ✅\nجرب الأوامر: /time /roll /pic /summarize /ai /whoami")

@bot.message_handler(commands=['time'])
def send_time(message):
    now = datetime.datetime.now()
    bot.reply_to(message, f"🕒 الوقت الآن: {now.strftime('%Y-%m-%d %H:%M:%S')}")

@bot.message_handler(commands=['roll'])
def send_roll(message):
    number = random.randint(1, 100)
    bot.reply_to(message, f"🎲 رقم عشوائي: {number}")

@bot.message_handler(commands=['pic'])
def send_picture(message):
    pics = [
        "https://picsum.photos/200/300",
        "https://picsum.photos/300/300",
        "https://picsum.photos/400/300",
    ]
    bot.send_photo(message.chat.id, random.choice(pics))

@bot.message_handler(commands=['summarize'])
def summarize_text(message):
    text = message.text[len('/summarize '):].strip()
    if not text:
        bot.reply_to(message, "✏️ أرسل نص بعد /summarize لتلخيصه.")
        return
    sentences = text.split('.')
    summary = '.'.join(sentences[:2]) + '.' if len(sentences) > 2 else text
    bot.reply_to(message, f"📝 الملخص:\n{summary}")

@bot.message_handler(commands=['ai'])
def openai_response(message):
    if not OPENAI_API_KEY:
        bot.reply_to(message, "⚠️ لم يتم إعداد مفتاح OpenAI API")
        return
    prompt = message.text[len('/ai '):].strip()
    if not prompt:
        bot.reply_to(message, "✏️ اكتب سؤال بعد /ai")
        return
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        result = response.json()
        answer = result['choices'][0]['message']['content']
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {e}")

@bot.message_handler(commands=['whoami'])
def who_am_i(message):
    try:
        url = "http://g.net/status?var=callBack"
        headers = {
            "Host": "g.net",
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
        }
        cookies = {
            "userxx": "3293972607",  # عدّل حسب الحاجة
            "speed": "512K/1M"
        }

        response = requests.get(url, headers=headers, cookies=cookies, timeout=5)
        data = response.json()

        msg = (
            f"📛 اسم المستخدم: {data['username']}\n"
            f"💻 MAC: {data['mac'].replace('%3A', ':')}\n"
            f"🌐 IP: {data['ip']}\n"
            f"📶 السرعة: {data['myspeed']}\n"
            f"📥 البيانات الواردة: {data['bytes_in']}\n"
            f"📤 البيانات الصادرة: {data['bytes_out']}\n"
            f"⏱ الوقت المتبقي: {data['session_time_left']}\n"
            f"⏳ مدة الاتصال: {data['uptime']}\n"
            f"🧪 تجريبي؟: {data['trial']}"
        )
        bot.reply_to(message, f"✅ البيانات:\n{msg}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل في الاتصال:\n{e}")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    save_user(message.from_user)
    bot.reply_to(message, f"📣 قلت: {message.text}")

print("🤖 البوت يعمل الآن...")
bot.polling()
