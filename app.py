from flask import Flask, request, jsonify
import os
import requests

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
    data = request.get_json()
    
    if 'entry' not in data:
        return jsonify({"status": "ignored"}), 200
    
    try:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                
                for msg in messages:
                    if 'text' in msg:
                        from_number = msg.get('from', '')
                        message_body = msg.get('text', {}).get('body', '')
                        
                        # Auto reply
                        reply = f"Kamu kirim: {message_body}\nTerima kasih sudah chat!"
                        send_whatsapp_message(from_number, reply)
    except Exception as e:
        print(f"Error: {e}")
    
    return jsonify({"status": "received"}), 200

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