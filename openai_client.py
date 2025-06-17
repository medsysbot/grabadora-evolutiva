import os
try:
    import openai
except Exception:  # pragma: no cover - library opcional
    openai = None


def consultar_openai(mensaje_usuario: str) -> str:
    """Consulta a OpenAI usando GPT-4o y devuelve la respuesta."""
    if openai is None:
        return "Error: librería OpenAI no disponible"

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
        return respuesta['choices'][0]['message']['content']
    except Exception as e:
        return f"Error al conectar con OpenAI: {e}"
