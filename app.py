from flask import Flask, request
import os
import requests
from openai import OpenAI

app = Flask(__name__)

VERIFY_TOKEN = "asistentevc123"
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PHONE_NUMBER_ID = "732770036577471"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Eres la Asistente de V&C, recepcionista virtual de la clínica dental V&C Odontólogos en Perú. 
Saluda con amabilidad, responde dudas frecuentes, ofrece información sobre tratamientos como carillas, implantes, brackets y limpieza dental.
Nunca respondas fuera del rol de asistente clínica.
"""

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if (request.args.get("hub.mode") == "subscribe" and
            request.args.get("hub.verify_token") == VERIFY_TOKEN):
            return request.args.get("hub.challenge"), 200
        return "Unauthorized", 403

    if request.method == "POST":
        data = request.get_json()
        print("📅 Webhook recibido:", data)

        try:
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if not messages:
                print("⚠️ No hay mensajes. Probablemente fue una reacción o mensaje de sistema.")
                return "EVENT_RECEIVED", 200

            message = messages[0]
            user_text = message["text"]["body"]
            sender = message["from"]
            print("🗣 Usuario dijo:", user_text)

            chat_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ]
            )

            reply_text = chat_response.choices[0].message.content.strip()
            print("🤖 GPT respondió:", reply_text)

            url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": sender,
                "text": {"body": reply_text}
            }

            print("📤 Enviando a WhatsApp:", payload)
            response = requests.post(url, headers=headers, json=payload)
            print("📬 Respuesta de WhatsApp:", response.status_code, response.text)

        except Exception as e:
            print("❌ Error general:", e)

        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
