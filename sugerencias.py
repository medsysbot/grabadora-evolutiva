import os
import json
import datetime

LOG_DIR = "logs"
ACTIVIDAD_LOG = os.path.join(LOG_DIR, "actividad.log")
PENDIENTES_FILE = os.path.join(LOG_DIR, "sugerencias_pendientes.json")
APLICADAS_FILE = os.path.join(LOG_DIR, "sugerencias_aplicadas.json")
RECHAZADAS_FILE = os.path.join(LOG_DIR, "sugerencias_rechazadas.json")
CODIGO_FILE = os.path.join(LOG_DIR, "sugerencias_codigo.json")


def asegurar_archivos():
    """Garantiza la existencia de todos los archivos de log."""
    os.makedirs(LOG_DIR, exist_ok=True)
    archivos = {
        ACTIVIDAD_LOG: "",
        PENDIENTES_FILE: "[]",
        APLICADAS_FILE: "[]",
        RECHAZADAS_FILE: "[]",
        CODIGO_FILE: "[]",
    }
    for ruta, contenido in archivos.items():
        if not os.path.exists(ruta):
            with open(ruta, "w") as f:
                f.write(contenido)


def _leer_lista(path):
    asegurar_archivos()
    with open(path) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _guardar_lista(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def guardar_pendiente(texto: str) -> dict:
    """Agrega una nueva sugerencia a la lista de pendientes."""
    pendientes = _leer_lista(PENDIENTES_FILE)
    sugerencia = {
        "id": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "texto": texto,
        "estado": "pendiente",
    }
    pendientes.append(sugerencia)
    _guardar_lista(PENDIENTES_FILE, pendientes)
    return sugerencia


def obtener_pendientes() -> list:
    return _leer_lista(PENDIENTES_FILE)


def guardar_pendientes(data: list) -> None:
    _guardar_lista(PENDIENTES_FILE, data)


def _mover(id_sug: str, origen: str, destino: str) -> dict | None:
    lista_origen = _leer_lista(origen)
    sugerencia = next((s for s in lista_origen if s.get("id") == id_sug), None)
    if not sugerencia:
        return None
    lista_origen = [s for s in lista_origen if s.get("id") != id_sug]
    _guardar_lista(origen, lista_origen)

    lista_destino = _leer_lista(destino)
    lista_destino.append(sugerencia)
    _guardar_lista(destino, lista_destino)
    return sugerencia


def mover_a_aplicadas(id_sugerencia: str) -> dict | None:
    """Mueve la sugerencia indicada a la lista de aplicadas."""
    return _mover(id_sugerencia, PENDIENTES_FILE, APLICADAS_FILE)


def mover_a_rechazadas(id_sugerencia: str) -> dict | None:
    """Mueve la sugerencia indicada a la lista de rechazadas."""
    return _mover(id_sugerencia, PENDIENTES_FILE, RECHAZADAS_FILE)


def registrar_codigo(id_sug: str, texto: str, codigo: str) -> None:
    """Guarda el código generado para una sugerencia aplicada."""
    lista = _leer_lista(CODIGO_FILE)
    lista.append({
        "id": id_sug,
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sugerencia": texto,
        "codigo": codigo,
    })
    _guardar_lista(CODIGO_FILE, lista)
