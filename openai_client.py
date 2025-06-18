import os
from datetime import datetime
try:
    import openai
except Exception:  # pragma: no cover - library opcional
    openai = None

# ╔════════════════════════════════════════════════════════════╗
# ║            CONFIGURACIÓN Y CONTROL DE CONSUMO             ║
# ╚════════════════════════════════════════════════════════════╝

TOPE_MENSUAL = 50
ARCHIVO_CONSUMO = "consumo_mes.txt"
ARCHIVO_FECHA = "mes_actual.txt"


def obtener_consumo() -> int:
    """Devuelve la cantidad de consultas registradas este mes."""
    if not os.path.exists(ARCHIVO_CONSUMO):
        with open(ARCHIVO_CONSUMO, "w") as f:
            f.write("0")
        return 0
    with open(ARCHIVO_CONSUMO, "r") as f:
        contenido = f.read().strip() or "0"
    return int(contenido)


def registrar_consulta() -> None:
    """Incrementa en uno el contador de consultas del mes."""
    consumo = obtener_consumo() + 1
    with open(ARCHIVO_CONSUMO, "w") as f:
        f.write(str(consumo))


def resetear_consumo_si_cambio_el_mes() -> None:
    """Reinicia el contador si comenzó un nuevo mes."""
    mes_actual = datetime.now().strftime("%Y-%m")
    if not os.path.exists(ARCHIVO_FECHA) or open(ARCHIVO_FECHA).read().strip() != mes_actual:
        with open(ARCHIVO_CONSUMO, "w") as f:
            f.write("0")
        with open(ARCHIVO_FECHA, "w") as f:
            f.write(mes_actual)


def puede_consultar() -> bool:
    """Indica si aún no se alcanzó el tope mensual."""
    resetear_consumo_si_cambio_el_mes()
    return obtener_consumo() < TOPE_MENSUAL

# ╔════════════════════════════════════════════════════════════╗
# ║                 CONSULTA A OPENAI CON LÍMITE               ║
# ╚════════════════════════════════════════════════════════════╝

def consultar_openai(mensaje_usuario: str) -> str:
    """Consulta a OpenAI usando GPT-4o si no se superó el tope."""
    if openai is None:
        return "Error: librería OpenAI no disponible"

    if not puede_consultar():
        return "Tope mensual alcanzado, no se realizará la consulta."

    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sos un asistente técnico que ayuda a reparar sistemas digitales."},
                {"role": "user", "content": mensaje_usuario}
            ],
            temperature=0.7,
            max_tokens=400
        )
        registrar_consulta()
        return respuesta['choices'][0]['message']['content']
    except Exception as e:
        return f"Error al conectar con OpenAI: {e}"
