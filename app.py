from flask import Flask, request
import os
import requests
import openai

app = Flask(__name__)

VERIFY_TOKEN = "asistentevc123"
PAGE_ACCESS_TOKEN = "EAAUNeE6PkcMBO3AZBYk49e64w3sgnloBLAZCpWgP7FIsMETvoZBlH9bN8mfwFzbwZCZA69zr39UIDAcqBSxrKvx7VPzHbvVxhHZA9QUX6YrFeIOsIX1Hf2yPGcp6IoCQVu5CZBRsvVm8hhWjEFZAWI6gEB4YldZBfyzETpyIXREUZBBNgLyCCYxZCmAEZAxeVIg3QvDAsz0aYZB58bLlEhDfFOkJHAFqzVCZAJqItLZCYlrDzJQWBmZB"
PHONE_NUMBER_ID = "732770036577471"

openai.api_key = os.getenv("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")

SYSTEM_PROMPT = """
Eres la Asistente de V&C, recepcionista virtual de la clínica dental V&C Odontólogos en Perú...
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
        print("✅ Webhook recibido:", data)

        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            user_text = message["text"]["body"]
            sender = message["from"]

            print("🗣 Usuario:", user_text)

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ]
            )

            reply_text = response.choices[0].message.content.strip()
            print("🤖 Respuesta GPT:", reply_text)

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

            r = requests.post(url, headers=headers, json=payload)
            print("📬 Resultado:", r.status_code, r.text)

        except Exception as e:
            print("❌ Error:", e)

        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

