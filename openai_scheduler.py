"""Ejecuta consultas automáticas a OpenAI en horarios predefinidos."""

import time
import schedule
from openai_client import consultar_openai

# Días y horas de consulta. Modificar para cambiar la frecuencia.
FRECUENCIA = {
    "monday": "10:00",
    "wednesday": "10:00",
    "friday": "10:00",
}

MENSAJE_AUTOMATICO = "Consulta automática programada"


def _tarea():
    respuesta = consultar_openai(MENSAJE_AUTOMATICO)
    print(f"Respuesta IA: {respuesta}")


def programar_consultas(frecuencia: dict = FRECUENCIA):
    """Registra en schedule los días y horas definidos."""
    for dia, hora in frecuencia.items():
        getattr(schedule.every(), dia).at(hora).do(_tarea)


def ejecutar():
    """Inicia el bucle que verifica tareas pendientes."""
    programar_consultas()
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    ejecutar()
