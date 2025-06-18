import os
import json
import datetime

LOG_DIR = "logs"
PENDIENTES_FILE = os.path.join(LOG_DIR, "sugerencias_pendientes.json")
APLICADAS_FILE = os.path.join(LOG_DIR, "sugerencias_aplicadas.json")


def _leer(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def _guardar(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def guardar_pendiente(texto: str) -> dict:
    pendientes = _leer(PENDIENTES_FILE)
    sugerencia = {
        "id": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "texto": texto,
        "estado": "pendiente",
    }
    pendientes.append(sugerencia)
    _guardar(PENDIENTES_FILE, pendientes)
    return sugerencia


def obtener_pendientes() -> list:
    return _leer(PENDIENTES_FILE)


def guardar_pendientes(data: list) -> None:
    _guardar(PENDIENTES_FILE, data)


def agregar_aplicada(sugerencia: dict) -> None:
    aplicadas = _leer(APLICADAS_FILE)
    aplicadas.append(sugerencia)
    _guardar(APLICADAS_FILE, aplicadas)
