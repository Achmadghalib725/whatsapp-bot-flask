from flask import Flask, request, jsonify
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Environment variables - set di Railway dashboard
TWILIO_SID = os.getenv('TWILIO_SID', '')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN', '')
TWILIO_PHONE = os.getenv('TWILIO_PHONE', '')

# Nous Portal (OpenAI-compatible) inference API
NOUS_API_KEY = os.getenv('NOUS_API_KEY', '')
NOUS_BASE_URL = os.getenv('NOUS_BASE_URL', 'https://inference-api.nousresearch.com/v1')
NOUS_MODEL = os.getenv('NOUS_MODEL', 'deepseek/deepseek-v4-flash')

SYSTEM_PROMPT = (
    "Kamu asisten WhatsApp yang ramah. Jawab singkat dalam bahasa Indonesia "
    "kecuali user memakai bahasa lain."
)
FALLBACK_REPLY = "Maaf, asisten AI sedang tidak tersedia. Coba lagi sebentar."
MAX_REPLY_CHARS = 1500


def ask_ai(user_text):
    try:
        resp = requests.post(
            f"{NOUS_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {NOUS_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": NOUS_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
                "max_tokens": 500,
                "tags": ["user=whatsapp-bot"],
            },
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"Nous API error: {resp.status_code} {resp.text}")
            return FALLBACK_REPLY
        content = resp.json()["choices"][0]["message"]["content"]
        if not content or not content.strip():
            print(f"Nous API empty content: {resp.status_code} {resp.text}")
            return FALLBACK_REPLY
        return content.strip()
    except Exception as e:
        print(f"Nous API exception: {e}")
        return FALLBACK_REPLY

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "whatsapp-bot"})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Twilio sends incoming messages as form-encoded data
        body = request.values.get('Body', '')
        from_number = request.values.get('From', '')  # e.g. whatsapp:+62...

        if not body or not from_number:
            return jsonify({"status": "ignored"}), 200

        reply = ask_ai(body)[:MAX_REPLY_CHARS]

        # Reply via TwiML so Twilio delivers the message
        resp = MessagingResponse()
        resp.message(reply)
        return str(resp), 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 200

def send_whatsapp_message(to, message):
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
        data = {
            'From': f'whatsapp:{TWILIO_PHONE}',
            'To': f'whatsapp:{to}',
            'Body': message
        }
        resp = requests.post(url, data=data, auth=(TWILIO_SID, TWILIO_TOKEN))
        print(f"Twilio response: {resp.status_code}")
    except Exception as e:
        print(f"Send message error: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)