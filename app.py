from flask import Flask, request, jsonify
import os
import requests

app = Flask(name)

Konfigurasi Twilio
TWILIO_SID     = os.getenv('TWILIO_SID')
TWILIO_TOKEN   = os.getenv('TWILIO_TOKEN')
TWILIO_PHONE   = os.getenv('TWILIO_PHONE')

Konfigurasi Ollama AI
OLLAMA_URL     = 'http://localhost:11434/api/chat'
MODEL_NAME     = 'laguna-xs-2.1:free'

def send_whatsapp(to, msg):
    """Kirim reply ke WhatsApp lewat Twilio"""
    if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_PHONE]):
        print("Missing Twilio config!")
        return
    try:
        url = f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.xml'
        data = {'From': f'whatsapp:{TWILIO_PHONE}', 'To': f'whatsapp:{to}', 'Body': msg}
        requests.post(url, data=data, auth=(TWILIO_SID, TWILIO_TOKEN), timeout=10)
    except Exception as e:
        print(f"Twilio error: {e}")

def ollama_chat(prompt):
    """Panggil model AI lewat Ollama"""
    try:
        payload = {
            'model': MODEL_NAME,
            'messages': [{'role': 'user', 'content': prompt}],
            'stream': False,
            'options': {'temperature': 0.7, 'num_predict': 256}
        }
        r = requests.post(OLLAMA_URL, json=payload, timeout=90)
        result = r.json()
        if 'message' in result:
            return result['message']['content'].strip()
        return str(result)
    except Exception as e:
        return f"AI Error: {e}"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'ai': 'active', 'model': MODEL_NAME})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = msg.get('from', '')
        text = msg.get('text', {}).get('body', '')

        if sender and text:
            ai_reply = ollama_chat(text)
            print(f"AI Reply: {ai_reply[:100]}...")
            send_whatsapp(sender, ai_reply)
    except Exception as e:
        print(f"Webhook error: {e}")

    return '', 200

if name == 'main':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
