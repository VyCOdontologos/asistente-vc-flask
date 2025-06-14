from flask import Flask, request
import os
import requests
from openai import OpenAI

app = Flask(__name__)

VERIFY_TOKEN = "asistentevc123"
PAGE_ACCESS_TOKEN = "EAAUNeE6PkcMBO7keMORSFpqdIynd3i3rOu8W2a9ADTZC4nsmVqe4tGpZAFdaa6vRbAGe6Q9Y0k6ERSuRZCfwqZAQmA5EGLnXf2A2dmaxSVZBDZBrKO7DQscnY0btw0gG9PdJfZBklYi4g6K33r530NNffRdIz1uPuohZBEmCDqZBvOc9joeOe9KDjYaMlJjNfeppnW0NZBz7kiS8GvJlsU8SQUxJrnYIRZB5qjIw4vAoLNIry57qQZDZD"
PHONE_NUMBER_ID = "2455358288176116"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Eres la Asistente de V&C, recepcionista virtual de la clínica dental V&C Odontólogos en Perú. Tu tono es cordial, claro y empático. Usa emojis moderadamente. Brindas información sobre implantes dentales, carillas, brackets, prótesis, limpieza, cirugía de terceros molares y más. La evaluación general cuesta S/60 y la especializada S/100. Recuerda indicar que se requiere tomografía para implantes y que la clínica cuenta con equipo propio para tomografía, panorámicas, cefalométricas y periapicales.
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
        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            user_text = message["text"]["body"]
            sender = message["from"]

            # Obtener respuesta desde OpenAI
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ]
            )
            reply_text = response.choices[0].message.content

            # Enviar respuesta a WhatsApp Cloud API
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
            requests.post(url, headers=headers, json=payload)

        except Exception as e:
            print("Error:", e)
        return "EVENT_RECEIVED", 200

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

