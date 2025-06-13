from flask import Flask, request
import os
import openai
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
Eres la Asistente de V&C, recepcionista virtual de la clínica dental V&C Odontólogos en Perú. Tu tono es cordial, claro y empático. Usa emojis moderadamente. Brindas información sobre implantes dentales, carillas, brackets, prótesis, limpieza, cirugía de terceros molares y más. La evaluación general cuesta S/60 y la especializada S/100. Recuerda indicar que se requiere tomografía para implantes y que la clínica cuenta con equipo propio para tomografía, panorámicas, cefalométricas y periapicales.
"""

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming = request.form.get("Body", "")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": incoming}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    reply = response.choices[0].message.content
    twilio_response = MessagingResponse()
    twilio_response.message(reply)
    return str(twilio_response)

if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
