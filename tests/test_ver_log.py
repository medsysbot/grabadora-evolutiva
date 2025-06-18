import os
from fastapi.testclient import TestClient
from main import app, LOG_FILES

client = TestClient(app)


def test_ver_log_crea_json(tmp_path):
    nombre = "sugerencias_pendientes.json"
    ruta = LOG_FILES[nombre]
    if os.path.exists(ruta):
        os.remove(ruta)
    resp = client.get(f"/ver_log?archivo={nombre}")
    assert resp.status_code == 200
    assert resp.json() == []
    assert os.path.exists(ruta)


def test_ver_log_crea_texto(tmp_path):
    nombre = "actividad.log"
    ruta = LOG_FILES[nombre]
    if os.path.exists(ruta):
        os.remove(ruta)
    resp = client.get(f"/ver_log?archivo={nombre}")
    assert resp.status_code == 200
    assert "actividad.log" in resp.text
    assert os.path.exists(ruta)
