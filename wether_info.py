import os
import requests
from flask import Flask, request

# -----------------------------
# CONFIG
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")

WEBHOOK_URL = f"https://your-app-name.onrender.com/{BOT_TOKEN}"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

app = Flask(__name__)

# -----------------------------
# Weather Info Function
# -----------------------------
def get_weather(place: str) -> str:
    try:
        params = {
            "q": f"{place},BD",
            "appid": WEATHER_KEY,
            "units": "metric",
            "lang": "en"
        }
        res = requests.get(WEATHER_URL, params=params, timeout=5).json()
        if res.get("cod") != 200:
            return f"❌ Not found: {res.get('message','Unknown error')}"

        # Weather Icons
        weather_icon = {
            "clear": "☀️",
            "clouds": "☁️",
            "rain": "🌧",
            "drizzle": "💧",
            "thunderstorm": "⛈",
            "snow": "❄️",
            "mist": "🌫"
        }
        desc = res['weather'][0]['description']
        main_desc = res['weather'][0]['main'].lower()
        icon = weather_icon.get(main_desc, "🌡️")

        return (
            "┏━━━━━━━━━━━━━━━━━┓\n"
            "    🌐 H4ck3r We4th3r Inf0 🌐\n"
            "┗━━━━━━━━━━━━━━━━━┛\n\n"
            f"📍 Location: `{res['name']}, {res['sys']['country']}`\n"
            f"{icon} Condition: `{desc}`\n"
            f"🌡 Temp: `{res['main']['temp']}°C` (Feels like {res['main']['feels_like']}°C)\n"
            f"💧 Humidity: `{res['main']['humidity']}%`\n"
            f"🌬 Wind: `{res['wind']['speed']} m/s`\n"
            f"🗺 Maps: https://www.google.com/maps?q={res['coord']['lat']},{res['coord']['lon']}\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "💀 Coded By: *SHADOW JOKER*"
        )
    except Exception as e:
        return f"⚠ Error: {e}"

# -----------------------------
# Send Message
# -----------------------------
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(API_URL + "sendMessage", json=payload)

# -----------------------------
# Flask Routes
# -----------------------------
@app.route("/")
def home():
    return "🤖 Weather Bot Running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if text == "/start":
            keyboard = {
                "inline_keyboard": [
                    [{"text": "Dhaka", "callback_data": "Dhaka"}],
                    [{"text": "Chittagong", "callback_data": "Chittagong"}],
                    [{"text": "Rajshahi", "callback_data": "Rajshahi"}],
                    [{"text": "Manual Input", "callback_data": "manual"}]
                ]
            }
            send_message(chat_id,
                         "👋 Welcome to Bangladesh Weather Bot!\n\n"
                         "🌐 Select your Upazila or choose Manual Input 🔥\n\n"
                         "💀 Powered By: *SHADOW JOKER*",
                         {"inline_keyboard": keyboard["inline_keyboard"]})

        elif "text" in msg:
            if text.lower() != "manual":
                info = get_weather(text)
                send_message(chat_id, info)

    elif "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data = query["data"]

        if data == "manual":
            send_message(chat_id, "✍️ Please type your Upazila/Thana name:")
        else:
            info = get_weather(data)
            send_message(chat_id, info)

    return "ok"

# -----------------------------
# Set Webhook Automatically
# -----------------------------
def set_webhook():
    res = requests.get(API_URL + "setWebhook", params={"url": WEBHOOK_URL})
    print("Webhook setup response:", res.json())

# -----------------------------
if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)