# Archivo: autodiagnostico.py
"""Ejecuta diagnósticos programados y guarda los resultados."""

import os
import datetime
import threading
from main import diagnostico, registrar_evento
from sugerencias import asegurar_archivos

LOG_DIR = "logs"
AUTO_LOG = os.path.join(LOG_DIR, "auto_diagnostico.log")

def ejecutar_autodiagnostico():
    """Llama a /diagnostico y registra su resultado."""
    asegurar_archivos()
    try:
        resultado = diagnostico()
    except Exception as e:
        resultado = f"Error al ejecutar diagnóstico: {e}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] Resultado del diagnóstico: {resultado}\n"
    with open(AUTO_LOG, "a") as f:
        f.write(linea)
    try:
        registrar_evento("Autodiagnóstico ejecutado")
    except Exception:
        pass

    # Programa la siguiente ejecución en 1 hora
    threading.Timer(3600, ejecutar_autodiagnostico).start()

if __name__ == "__main__":
    ejecutar_autodiagnostico()
