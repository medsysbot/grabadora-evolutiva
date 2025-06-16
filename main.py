# ╔════════════════════════════════════════════════════════════╗
# ║                      IMPORTACIONES                        ║
# ╚════════════════════════════════════════════════════════════╝

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import datetime

# ╔════════════════════════════════════════════════════════════╗
# ║                 CONFIGURACIÓN DE ARCHIVOS                 ║
# ╚════════════════════════════════════════════════════════════╝

app = FastAPI()

# Carpetas para HTML y JS
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Rutas de logs
LOG_FILE = "logs/errores.log"
ACTIVIDAD_LOG = "logs/actividad.log"

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
