from fastapi import FastAPI
import os
import datetime

app = FastAPI()
LOG_FILE = "../logs/errores.log"

def escribir_log(mensaje):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now()}: {mensaje}\n")

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
