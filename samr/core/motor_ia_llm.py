"""Motor de Inteligencia Artificial basado en Modelos LLM (Groq API en la nube con fallback a Ollama local y motor de reglas)."""
import json
import logging
import os
import re
import requests

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_TIMEOUT_SECS = 10

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "llama3.2"
OLLAMA_TIMEOUT_SECS = 15


def llamar_groq(prompt, modelo=DEFAULT_GROQ_MODEL):
    """
    Hace una petición POST a la API de Groq en la nube.
    Retorna el texto generado o None si la clave no existe o si falla la llamada.
    """
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        logger.warning("GROQ_API_KEY no está configurada o está vacía.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=GROQ_TIMEOUT_SECS)
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if choices and len(choices) > 0:
            return choices[0].get("message", {}).get("content", "")
        return None
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.warning(f"Groq API no responde o se agotó el tiempo: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.warning(f"Error HTTP en la API de Groq (clave inválida o rate limit): {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al llamar a Groq: {e}")
        return None


def llamar_ollama(prompt, modelo=DEFAULT_OLLAMA_MODEL):
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
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=OLLAMA_TIMEOUT_SECS)
        response.raise_for_status()
        return response.json().get("response", "")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.warning(f"Ollama no responde o no está disponible: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al llamar a Ollama: {e}")
        return None


def obtener_respuesta_llm(prompt):
    """
    Cadena de respaldo LLM:
    1. Intenta Groq API (nube).
    2. Si falla o devuelve None, intenta Ollama (local).
    3. Si ambos fallan, devuelve (None, None).
    Retorna la tupla: (texto_respuesta, identificador_modelo)
    """
    respuesta_groq = llamar_groq(prompt)
    if respuesta_groq:
        logger.info("Respuesta obtenida exitosamente desde Groq API.")
        return respuesta_groq, f"groq-{DEFAULT_GROQ_MODEL}"

    respuesta_ollama = llamar_ollama(prompt)
    if respuesta_ollama:
        logger.info("Respuesta obtenida exitosamente desde Ollama.")
        return respuesta_ollama, f"ollama-{DEFAULT_OLLAMA_MODEL}"

    logger.warning("Tanto Groq como Ollama fallaron o no están disponibles. Caerá al motor de reglas como respaldo.")
    return None, None


def clasificar_sintomas_llm(texto_sintomas):
    """
    Usa el LLM (Groq / Ollama) para clasificar síntomas.
    Retorna dict con nivel_urgencia, explicacion_xai, etc. o None si fallan los modelos.
    """
    prompt = f"""Eres un asistente de TRIAJE (no de diagnóstico). Tu única función es evaluar qué tan urgente es que el paciente sea visto por un médico, según la escala Manchester (1=emergencia inmediata, 5=no urgente).

REGLAS ESTRICTAS:
- NUNCA menciones el nombre de una enfermedad, condición médica o diagnóstico específico (prohibido decir cosas como 'es probable que tengas X', 'parece ser Y', nombres de enfermedades)
- Tu explicación debe describir SOLO qué síntomas identificaste y por qué ameritan ese nivel de urgencia, en lenguaje simple
- Nunca dés consejos de tratamiento (medicamentos, remedios)
- Si no estás seguro del nivel, sé conservador (asigna mayor urgencia, no menor)

Responde ÚNICAMENTE en JSON con esta estructura exacta, sin texto adicional ni antes ni después:
{{
    "nivel_urgencia": <1-5>,
    "sintomas_detectados": ["sintoma1", "sintoma2"],
    "explicacion": "Explicación médica breve y clara orientada al paciente de los síntomas y urgencia"
}}

Síntomas del paciente: {texto_sintomas}"""

    respuesta, id_modelo = obtener_respuesta_llm(prompt)
    if not respuesta:
        return None

    logger.info(f"LLM ({id_modelo}) raw response: {respuesta}")

    try:
        match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if not match:
            logger.warning(f"No se encontró formato JSON en la respuesta de {id_modelo}.")
            return None
            
        data = json.loads(match.group(0))
        
        nivel_urgencia = int(data.get("nivel_urgencia", 5))
        if nivel_urgencia < 1 or nivel_urgencia > 5:
            nivel_urgencia = 5
            
        explicacion = str(data.get("explicacion", "Evaluación procesada correctamente."))
        disclaimer = " Esta es una evaluación preliminar de urgencia, no un diagnóstico — el médico asignado confirmará tu condición."
        if disclaimer not in explicacion:
            explicacion += disclaimer
            
        sintomas = data.get("sintomas_detectados", [])
        
        return {
            "nivel_urgencia": nivel_urgencia,
            "explicacion_xai": explicacion,
            "confianza": 0.95,
            "version_modelo": id_modelo,
            "sintomas_detectados": sintomas
        }
    except Exception as e:
        logger.error(f"Error parseando respuesta JSON de {id_modelo}: {e}\nRespuesta cruda: {respuesta}")
        return None


def responder_chat_llm(historial_previo, nuevo_mensaje, turno):
    """
    Genera una respuesta conversacional basada en el contexto previo mediante el LLM.
    """
    prompt = f"""Eres un asistente médico virtual empático encargado exclusivamente de TRIAJE.
Tu objetivo es recopilar información del paciente haciendo máximo una o dos preguntas claras y breves a la vez. No diagnostiques, solo indaga para clasificar.

REGLAS ESTRICTAS:
- NUNCA diagnostiques ni menciones posibles enfermedades.
- Nunca dés consejos de tratamiento (medicamentos, remedios).

Debes responder en formato JSON exactamente con esta estructura:
{{
    "texto_respuesta": "Tu respuesta conversacional y empática aquí",
    "listo_para_clasificar": <true o false. Usa true si ya tienes suficiente información (ej. intensidad, duración) o si el turno es >= 2>
}}

Historial de la conversación (solo mensajes del paciente): {historial_previo}
Nuevo mensaje del paciente: {nuevo_mensaje}
Turno actual: {turno}

Recuerda, si turno es >= 2, debes poner listo_para_clasificar en true para terminar el chat."""

    respuesta, id_modelo = obtener_respuesta_llm(prompt)
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
        logger.error(f"Error parseando respuesta de chat de {id_modelo}: {e}")
        return None
