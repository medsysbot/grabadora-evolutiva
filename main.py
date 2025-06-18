# ╔════════════════════════════════════════════════════════════╗
# ║                      IMPORTACIONES                        ║
# ╚════════════════════════════════════════════════════════════╝

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
import datetime
from openai_client import consultar_openai
from openai import OpenAI
from sugerencias import (
    guardar_pendiente,
    obtener_pendientes,
    guardar_pendientes,
    agregar_aplicada,
)

# ╔════════════════════════════════════════════════════════════╗
# ║                 CONFIGURACIÓN DE ARCHIVOS                 ║
# ╚════════════════════════════════════════════════════════════╝

app = FastAPI()

# Carpetas para HTML y JS
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Directorios de trabajo
LOG_DIR = "logs"
CONTROL_DIR = "control"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CONTROL_DIR, exist_ok=True)

# Archivos de registro
LOG_FILE = os.path.join(LOG_DIR, "errores.log")
ACTIVIDAD_LOG = os.path.join(LOG_DIR, "actividad.log")

# Archivos de control
RUTAS_FILE = os.path.join(CONTROL_DIR, "rutas.txt")
AGENTES_FILE = os.path.join(CONTROL_DIR, "agentes.txt")
BITACORA_FILE = os.path.join(CONTROL_DIR, "bitacora.txt")

def inicializar_archivos():
    """Crea archivos básicos si aún no existen."""
    archivos_iniciales = {
        RUTAS_FILE: (
            "/               → GET  → index.html / static/script.js / main.py\n"
            "                 Muestra la interfaz principal de la grabadora.\n\n"
            "/diagnostico     → GET  → main.py\n"
            "                 Ejecuta diagnóstico del sistema y devuelve errores registrados.\n\n"
            "/reparar         → GET  → main.py\n"
            "                 Limpia el archivo de errores para reiniciar el estado lógico.\n"
        ),
        AGENTES_FILE: (
            "[Agente: Registrador de eventos]\n"
            "Rol: Escribe cada interacción del usuario en actividad.log\n"
            "Estado: Activo\n"
            "Archivos: main.py\n\n"
            "[Agente: Diagnóstico inteligente]\n"
            "Rol: Analiza el estado del sistema y sugiere mejoras automáticas\n"
            "Estado: Activo\n"
            "Archivos: main.py\n\n"
            "[Agente: Auto-mejorador]\n"
            "Rol: Llama a OpenAI y aplica correcciones automáticas\n"
            "Estado: Futuro\n"
            "Archivos esperados: diagnostico.py, analisis_ia.py\n"
        ),
        BITACORA_FILE: (
            f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] Bitácora iniciada.\n"
        ),
        os.path.join(LOG_DIR, "sugerencias_pendientes.json"): "[]",
        os.path.join(LOG_DIR, "sugerencias_aplicadas.json"): "[]",
    }

    for ruta, contenido in archivos_iniciales.items():
        if not os.path.exists(ruta):
            with open(ruta, "w") as f:
                f.write(contenido)

    # Garantizar existencia del log de actividad
    if not os.path.exists(ACTIVIDAD_LOG):
        open(ACTIVIDAD_LOG, "a").close()

inicializar_archivos()

# ╔════════════════════════════════════════════════════════════╗
# ║           FUNCIONES DE REGISTRO DE ACTIVIDAD              ║
# ╚════════════════════════════════════════════════════════════╝


def registrar_evento(mensaje: str):
    """Guarda un evento de actividad con marca temporal."""
    os.makedirs(os.path.dirname(ACTIVIDAD_LOG), exist_ok=True)
    try:
        with open(ACTIVIDAD_LOG, "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {mensaje}\n")
    except Exception as e:
        print(f"Error al registrar actividad: {e}")

# ╔════════════════════════════════════════════════════════════╗
# ║                         RUTAS                             ║
# ╚════════════════════════════════════════════════════════════╝

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/diagnostico")
def diagnostico():
    registrar_evento("Se ejecutó diagnóstico del sistema.")
    if not os.path.exists(LOG_FILE):
        return "Todo parece estar en orden."
    with open(LOG_FILE) as f:
        contenido = f.read()
    return contenido or "Sin errores detectados."

@app.get("/reparar")
def reparar():
    registrar_evento("Se ejecutó reparación del sistema.")
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        return "Log de errores limpiado. Sistema reiniciado lógicamente."
    return "No hay errores a reparar."

@app.post("/registrar")
async def registrar_desde_frontend(request: Request):
    data = await request.json()
    mensaje = data.get("mensaje", "Evento no especificado.")
    registrar_evento(f"Desde frontend: {mensaje}")
    return {"status": "ok", "registrado": mensaje}


@app.post("/consultar")
async def consultar_openai_backend(request: Request):
    data = await request.json()
    pregunta = data.get("mensaje", "")
    respuesta = consultar_openai(pregunta)
    registrar_evento(f"Consulta IA: {pregunta} → {respuesta[:60]}...")
    return {"respuesta": respuesta}


@app.get("/historial", response_class=HTMLResponse)
async def ver_historial(request: Request):
    """Devuelve una página con el historial de actividad."""
    registrar_evento("Se consultó el historial")
    if not os.path.exists(ACTIVIDAD_LOG):
        eventos = []
    else:
        with open(ACTIVIDAD_LOG) as f:
            eventos = [line.strip() for line in f if line.strip()]
    return templates.TemplateResponse(
        "historial.html", {"request": request, "eventos": eventos}
    )

# ╔════════════════════════════════════════════════════════════╗
# ║      RUTA: /consultar_mejora_manual (POST desde web)       ║
# ╚════════════════════════════════════════════════════════════╝

@app.post("/consultar_mejora_manual")
async def consultar_mejora_manual():
    log_path = "logs/actividad.log"
    if not os.path.exists(log_path):
        actividad = "No hay actividad registrada aún."
    else:
        with open(log_path, "r") as f:
            actividad = f.read()

    prompt = (
        "Este es el registro de actividad del sistema:\n"
        f"{actividad}\n"
        "¿Qué sugerencias de mejora, robustez o evolución recomendarías para esta aplicación de grabadora de voz autónoma?"
    )
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    respuesta = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Sos un arquitecto digital que da consejos técnicos de mejora."},
            {"role": "user", "content": prompt}
        ]
    ).choices[0].message.content.strip()

    log_mejoras = "logs/mejoras_sugeridas.log"
    with open(log_mejoras, "a") as f:
        import time
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {respuesta}\n")
    guardar_pendiente(respuesta)
    return {"respuesta": respuesta}


@app.get("/sugerencias_pendientes")
def sugerencias_pendientes():
    import json, os
    archivo = "logs/sugerencias_pendientes.json"
    if not os.path.exists(archivo):
        return []
    with open(archivo) as f:
        return json.load(f)


@app.post("/aplicar_sugerencia")
async def aplicar_sugerencia(request: Request):
    """Marca una sugerencia como aplicada y genera el código recomendado."""
    import json, os, time
    from openai import OpenAI

    data = await request.json()
    sugerencia_id = data.get("id")

    pendientes_file = "logs/sugerencias_pendientes.json"
    aplicadas_file = "logs/sugerencias_aplicadas.json"
    codigo_file = "logs/sugerencias_codigo.json"

    with open(pendientes_file) as f:
        pendientes = json.load(f)

    sugerencia = next((s for s in pendientes if s["id"] == sugerencia_id), None)
    pendientes = [s for s in pendientes if s["id"] != sugerencia_id]

    with open(pendientes_file, "w") as f:
        json.dump(pendientes, f, indent=2)

    if not sugerencia:
        return {"status": "error", "msg": "Sugerencia no encontrada."}

    sugerencia["estado"] = "aplicada"

    if not os.path.exists(aplicadas_file):
        aplicadas = []
    else:
        with open(aplicadas_file) as f:
            aplicadas = json.load(f)
    aplicadas.append(sugerencia)
    with open(aplicadas_file, "w") as f:
        json.dump(aplicadas, f, indent=2)

    with open("logs/actividad.log", "a") as f:
        f.write(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Se aplicó sugerencia de IA: {sugerencia['texto']}\n"
        )

    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = (
        "La siguiente sugerencia de mejora fue aceptada: '"
        + sugerencia["texto"]
        + "'. Mi aplicación está hecha en HTML, JavaScript y Python (FastAPI). "
        "Por favor, generá el código necesario para implementar esta mejora. "
        "Decime claramente qué archivo debo modificar y dónde pegar el código, con comentarios y recomendaciones."
    )

    respuesta = (
        openai.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": "Sos un arquitecto digital que escribe código y explica cambios.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        .choices[0]
        .message.content.strip()
    )

    if not os.path.exists(codigo_file):
        codigos = []
    else:
        with open(codigo_file) as f:
            codigos = json.load(f)

    codigos.append(
        {
            "id": sugerencia["id"],
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sugerencia": sugerencia["texto"],
            "codigo": respuesta,
        }
    )
    with open(codigo_file, "w") as f:
        json.dump(codigos, f, indent=2, ensure_ascii=False)

    return {"status": "ok", "codigo": respuesta}


@app.post("/descartar_sugerencia")
async def descartar_sugerencia(request: Request):
    import json, os
    data = await request.json()
    sugerencia_id = data.get("id")
    pendientes_file = "logs/sugerencias_pendientes.json"

    with open(pendientes_file) as f:
        pendientes = json.load(f)
    pendientes = [s for s in pendientes if s["id"] != sugerencia_id]
    with open(pendientes_file, "w") as f:
        json.dump(pendientes, f, indent=2)
    with open("logs/actividad.log", "a") as f:
        import time
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Se descartó sugerencia de IA: {sugerencia_id}\n")
    return {"status": "ok"}
