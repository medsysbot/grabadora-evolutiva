# ╔════════════════════════════════════════════════════════════╗
# ║                      IMPORTACIONES                        ║
# ╚════════════════════════════════════════════════════════════╝

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
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
    mover_a_aplicadas,
    mover_a_rechazadas,
    registrar_codigo,
    asegurar_archivos,
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
MEJORAS_LOG = os.path.join(LOG_DIR, "mejoras_sugeridas.log")
PENDIENTES_JSON = os.path.join(LOG_DIR, "sugerencias_pendientes.json")
APLICADAS_JSON = os.path.join(LOG_DIR, "sugerencias_aplicadas.json")
RECHAZADAS_JSON = os.path.join(LOG_DIR, "sugerencias_rechazadas.json")
CODIGO_JSON = os.path.join(LOG_DIR, "sugerencias_codigo.json")

LOG_FILES = {
    "actividad.log": ACTIVIDAD_LOG,
    "mejoras_sugeridas.log": MEJORAS_LOG,
    "sugerencias_pendientes.json": PENDIENTES_JSON,
    "sugerencias_aplicadas.json": APLICADAS_JSON,
    "sugerencias_rechazadas.json": RECHAZADAS_JSON,
    "sugerencias_codigo.json": CODIGO_JSON,
}

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
        MEJORAS_LOG: "",
    }

    for ruta, contenido in archivos_iniciales.items():
        if not os.path.exists(ruta):
            with open(ruta, "w") as f:
                f.write(contenido)

    # Garantizar archivos de logs y listas de sugerencias
    asegurar_archivos()

inicializar_archivos()

# ╔════════════════════════════════════════════════════════════╗
# ║           FUNCIONES DE REGISTRO DE ACTIVIDAD              ║
# ╚════════════════════════════════════════════════════════════╝


def registrar_evento(mensaje: str):
    """Guarda un evento de actividad con marca temporal."""
    asegurar_archivos()
    try:
        with open(ACTIVIDAD_LOG, "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {mensaje}\n")
    except Exception as e:
        print(f"Error al registrar actividad: {e}")


def generar_codigo_mejora(texto_sugerencia: str) -> str:
    """Consulta a OpenAI para obtener el código de la mejora aceptada."""
    openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = (
        "La siguiente sugerencia de mejora fue aceptada: "
        f"'{texto_sugerencia}'. "
        "Mi aplicación está hecha en HTML, JavaScript y Python (FastAPI). "
        "Por favor, generá el código necesario para implementar esta mejora. "
        "Decime claramente qué archivo debo modificar y dónde pegar el código, con comentarios y recomendaciones."
    )
    respuesta = openai.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "Sos un arquitecto digital que escribe código y explica cambios."},
            {"role": "user", "content": prompt},
        ],
    ).choices[0].message.content.strip()
    return respuesta

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


@app.get("/admin", response_class=HTMLResponse)
async def admin_logs(request: Request):
    """Muestra la página de administración de logs."""
    registrar_evento("Se accedió a administración de logs")
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/ver_log")
def ver_log(archivo: str):
    """Devuelve el contenido de un archivo de log."""
    nombre = os.path.basename(archivo)
    if nombre not in LOG_FILES:
        return PlainTextResponse("Archivo no permitido", status_code=400)
    ruta = LOG_FILES[nombre]
    asegurar_archivos()
    registrar_evento(f"Se consultó {nombre}")
    if ruta.endswith(".json"):
        with open(ruta) as f:
            contenido = f.read().strip() or "[]"
        try:
            data = json.loads(contenido)
        except json.JSONDecodeError:
            data = []
        return JSONResponse(data)
    with open(ruta) as f:
        texto = f.read()
    return PlainTextResponse(texto)

# ╔════════════════════════════════════════════════════════════╗
# ║      RUTA: /consultar_mejora_manual (POST desde web)       ║
# ╚════════════════════════════════════════════════════════════╝

@app.post("/consultar_mejora_manual")
async def consultar_mejora_manual():
    asegurar_archivos()
    log_path = ACTIVIDAD_LOG
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

    with open(MEJORAS_LOG, "a") as f:
        import time
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {respuesta}\n")
    guardar_pendiente(respuesta)
    return {"respuesta": respuesta}


@app.get("/sugerencias_pendientes")
def sugerencias_pendientes():
    asegurar_archivos()
    return obtener_pendientes()


@app.post("/aplicar_sugerencia")
async def aplicar_sugerencia(request: Request):
    """Marca una sugerencia como aplicada, genera código y registra todo."""
    import time

    data = await request.json()
    sugerencia_id = data.get("id")

    asegurar_archivos()
    sugerencia = mover_a_aplicadas(sugerencia_id)

    if not sugerencia:
        return {"status": "error", "msg": "Sugerencia no encontrada."}

    registrar_evento(f"Se aplicó sugerencia de IA: {sugerencia['texto']}")

    codigo = generar_codigo_mejora(sugerencia["texto"])
    registrar_codigo(sugerencia_id, sugerencia["texto"], codigo)

    return {"status": "ok", "codigo": codigo}


@app.post("/descartar_sugerencia")
async def descartar_sugerencia(request: Request):
    data = await request.json()
    sugerencia_id = data.get("id")

    asegurar_archivos()
    sugerencia = mover_a_rechazadas(sugerencia_id)

    if sugerencia:
        registrar_evento(
            f"Se descartó sugerencia de IA: {sugerencia_id}"
        )
    return {"status": "ok"}
