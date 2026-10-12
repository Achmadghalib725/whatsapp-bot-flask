from flask import Flask, request, jsonify
import os
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Environment variables - set di Railway dashboard
TWILIO_SID = os.getenv('TWILIO_SID', '')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN', '')
TWILIO_PHONE = os.getenv('TWILIO_PHONE', '')

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

        reply = f"Kamu kirim: {body}\nTerima kasih sudah chat!"

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