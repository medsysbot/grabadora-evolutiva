from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import datetime

app = FastAPI()

# Carpetas para HTML y JS
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

LOG_FILE = "logs/errores.log"

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/diagnostico")
def diagnostico():
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
