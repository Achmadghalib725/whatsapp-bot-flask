# WhatsApp Bot - Flask

WhatsApp messaging bot that auto-replies to incoming messages.

## Deploy ke Railway (Gratis)

1. Fork repo ini ke GitHub
2. Di Railway: New Project → Deploy from GitHub
3. Pilih repo `whatsapp-bot-flask`
4. Set Environment Variables:
   - `TWILIO_SID`
   - `TWILIO_TOKEN`
   - `TWILIO_PHONE` (nomor WA dari Twilio Sandbox)

## Webhook Handler

- Endpoint: `/webhook`
- Method: POST
- Auto reply: "Kamu kirim: [pesan]"

## Testing

Gunakan Twilio WhatsApp Sandbox dengan reply "join"
Kirim message ke nomor sandbox tersebut