import os
from fastapi.testclient import TestClient
from main import app, ACTIVIDAD_LOG

client = TestClient(app)

def test_registro_evento(tmp_path):
    if os.path.exists(ACTIVIDAD_LOG):
        os.remove(ACTIVIDAD_LOG)
    resp = client.post('/registrar', json={'mensaje': 'prueba'})
    assert resp.status_code == 200
    assert os.path.exists(ACTIVIDAD_LOG)
    with open(ACTIVIDAD_LOG) as f:
        contenido = f.read()
    assert 'prueba' in contenido
