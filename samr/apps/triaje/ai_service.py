import json
import requests
from django.conf import settings

SYSTEM_PROMPT = """
Eres el motor de razonamiento clinico Med-Gemini del sistema SAMR (Sistema de Atencion Medica Remota).
Analiza la descripcion de sintomas de un paciente y devuelve UNICAMENTE un JSON valido, sin texto adicional,
sin markdown, con esta estructura exacta:

{
  "sintomas": ["lista de sintomas clinicos identificados, en minusculas"],
  "prioridad": "alta" | "moderada" | "menor",
  "explicacion": "una o dos frases explicando la prioridad, en lenguaje comprensible para el paciente",
  "confianza": <numero entero entre 0 y 100>
}

Si el texto no describe sintomas reales (saludos, texto irrelevante o insuficiente), responde con
"sintomas": [] y "prioridad": "menor" con una explicacion pidiendo mas informacion.
No inventes sintomas que el paciente no menciono.
"""

def _respuesta_fallback(mensaje="No se pudo completar el analisis clinico en este momento."):
    return {"error": True, "mensaje": mensaje, "sintomas": [], "prioridad": "menor", "explicacion": "", "confianza": 0}

def _analizar_con_ollama(texto: str) -> dict:
    try:
        resp = requests.post(
            f"{settings.OLLAMA_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "system": SYSTEM_PROMPT,
                "prompt": texto,
                "stream": False,
                "format": "json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        raw_text = resp.json().get("response", "")
        data = json.loads(raw_text)
        data.setdefault("sintomas", [])
        data.setdefault("prioridad", "menor")
        data.setdefault("explicacion", "")
        data.setdefault("confianza", 0)
        return data
    except Exception:
        return _respuesta_fallback("El motor de IA local (Ollama) no esta disponible. Verifica que este corriendo.")

def _analizar_con_gemini(texto: str) -> dict:
    try:
        # Implementacion ya definida en el prompt anterior (SDK de Gemini)
        # ... llamar a la API real de Gemini con settings.GEMINI_API_KEY ...
        raise NotImplementedError("Pendiente de activar en produccion")
    except Exception:
        return _respuesta_fallback("El motor de IA (Gemini) no esta disponible en este momento.")

def analizar_sintomas_con_ia(texto: str) -> dict:
    """Punto unico de entrada. El endpoint y el frontend solo llaman a esta funcion."""
    if not texto or not texto.strip():
        return _respuesta_fallback("No se proporciono texto para analizar.")

    proveedor = getattr(settings, "AI_PROVIDER", "local")
    if proveedor == "gemini":
        return _analizar_con_gemini(texto)
    return _analizar_con_ollama(texto)
