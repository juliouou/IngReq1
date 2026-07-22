"""Motor de Inteligencia Artificial basado en Modelos Locales (Ollama)."""
import json
import logging
import re
import requests

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"
TIMEOUT_SECS = 15

def llamar_ollama(prompt, modelo=DEFAULT_MODEL):
    """
    Hace una petición POST a la API local de Ollama.
    Retorna el texto generado o None si falla.
    """
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=TIMEOUT_SECS)
        response.raise_for_status()
        return response.json().get("response", "")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.warning(f"Ollama no responde o no está disponible: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al llamar a Ollama: {e}")
        return None

def clasificar_sintomas_llm(texto_sintomas):
    """
    Usa el LLM para clasificar síntomas. Retorna dict con nivel_urgencia,
    explicacion_xai, etc. o None si falla.
    """
    prompt = f"""Eres un asistente de triaje médico experto (Med-Gemini).
Analiza los siguientes síntomas y responde ÚNICAMENTE en formato JSON con esta estructura exacta, sin texto adicional ni antes ni después:
{{
    "nivel_urgencia": <1-5, donde 1 es emergencia vital y 5 es no urgente (escala Manchester)>,
    "sintomas_detectados": ["sintoma1", "sintoma2"],
    "explicacion": "Explicación médica breve y clara orientada al paciente del porqué de esta urgencia"
}}

Síntomas del paciente: {texto_sintomas}"""

    respuesta = llamar_ollama(prompt)
    if not respuesta:
        return None

    try:
        match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if not match:
            logger.warning("No se encontró formato JSON en la respuesta de Ollama.")
            return None
            
        data = json.loads(match.group(0))
        
        nivel_urgencia = int(data.get("nivel_urgencia", 5))
        if nivel_urgencia < 1 or nivel_urgencia > 5:
            nivel_urgencia = 5
            
        explicacion = str(data.get("explicacion", "Evaluación procesada correctamente."))
        sintomas = data.get("sintomas_detectados", [])
        
        return {
            "nivel_urgencia": nivel_urgencia,
            "explicacion_xai": explicacion,
            "confianza": 0.95,
            "version_modelo": f"ollama-{DEFAULT_MODEL}",
            "sintomas_detectados": sintomas
        }
    except Exception as e:
        logger.error(f"Error parseando respuesta JSON de Ollama: {e}\nRespuesta cruda: {respuesta}")
        return None

def responder_chat_llm(historial_previo, nuevo_mensaje, turno):
    """
    Genera una respuesta conversacional basada en el contexto previo.
    """
    prompt = f"""Eres un asistente médico virtual empático. 
Tu objetivo es recopilar información del paciente haciendo máximo una o dos preguntas claras y breves a la vez. No diagnostiques, solo indaga para clasificar.
Debes responder en formato JSON exactamente con esta estructura:
{{
    "texto_respuesta": "Tu respuesta conversacional y empática aquí",
    "listo_para_clasificar": <true o false. Usa true si ya tienes suficiente información (ej. intensidad, duración) o si el turno es >= 2>
}}

Historial de la conversación (solo mensajes del paciente): {historial_previo}
Nuevo mensaje del paciente: {nuevo_mensaje}
Turno actual: {turno}

Recuerda, si turno es >= 2, debes poner listo_para_clasificar en true para terminar el chat."""

    respuesta = llamar_ollama(prompt)
    if not respuesta:
        return None

    try:
        match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if not match:
            return None
            
        data = json.loads(match.group(0))
        texto = data.get("texto_respuesta", "¿Puedes darme más detalles?")
        listo = bool(data.get("listo_para_clasificar", False))
        
        if turno >= 2:
            listo = True
            
        if listo:
            texto = "Gracias por la información. Ya he recopilado suficientes datos. Procesaré tu solicitud ahora para clasificarla y asignarte un médico."
            
        return {
            "texto_respuesta": texto,
            "listo_para_clasificar": listo,
            "resultado": None
        }
    except Exception as e:
        logger.error(f"Error parseando respuesta de chat de Ollama: {e}")
        return None
