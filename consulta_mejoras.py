import os
import schedule
import time
from openai import OpenAI

LOG_ACTIVIDAD = "logs/actividad.log"
LOG_MEJORAS = "logs/mejoras_sugeridas.log"


def obtener_actividad():
    if not os.path.exists(LOG_ACTIVIDAD):
        return "No hay actividad registrada aún."
    with open(LOG_ACTIVIDAD, "r") as f:
        return f.read()


def consultar_mejora_gpt():
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    actividad = obtener_actividad()
    prompt = (
        "Este es el registro de actividad del sistema:\n"
        f"{actividad}\n"
        "¿Qué sugerencias de mejora, robustez o evolución recomendarías para esta aplicación de grabadora de voz autónoma?"
    )
    respuesta = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Sos un arquitecto digital que da consejos técnicos de mejora."},
            {"role": "user", "content": prompt}
        ]
    ).choices[0].message.content.strip()
    os.makedirs(os.path.dirname(LOG_MEJORAS), exist_ok=True)
    with open(LOG_MEJORAS, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {respuesta}\n")
    # Opcional: también registrar en actividad
    with open(LOG_ACTIVIDAD, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Consulta automática de mejora a GPT-4.1\n")


# Programar la consulta para todos los martes a las 9:00
schedule.every().tuesday.at("09:00").do(consultar_mejora_gpt)

print("Consulta de mejoras programada todos los martes a las 09:00.")

if __name__ == "__main__":
    # Consulta inmediata (manual)
    consultar_mejora_gpt()
    print("Consulta manual de mejora realizada. Revisá logs/mejoras_sugeridas.log para ver la respuesta.")

while True:
    schedule.run_pending()
    time.sleep(60)
