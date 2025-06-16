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
ACTIVITY_LOG = "logs/actividad.log"

# ╔════════════════════════════════════════════════════════════╗
# ║                  FUNCIONES AUXILIARES                     ║
# ╚════════════════════════════════════════════════════════════╝


def registrar_evento(mensaje: str) -> None:
    """Registra un mensaje en el archivo de actividad con timestamp."""
    os.makedirs(os.path.dirname(ACTIVITY_LOG), exist_ok=True)
    marca_tiempo = datetime.datetime.now().isoformat()
    with open(ACTIVITY_LOG, "a", encoding="utf-8") as log:
        log.write(f"{marca_tiempo} - {mensaje}\n")

# ╔════════════════════════════════════════════════════════════╗
# ║                         RUTAS                             ║
# ╚════════════════════════════════════════════════════════════╝

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/diagnostico")
def diagnostico():
    registrar_evento("Consulta de diagnostico")
    if not os.path.exists(LOG_FILE):
        return "Todo parece estar en orden."
    with open(LOG_FILE) as f:
        contenido = f.read()
    return contenido or "Sin errores detectados."

@app.get("/reparar")
def reparar():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        return "Log de errores limpiado. Sistema reiniciado lógicamente."
    return "No hay errores a reparar."
