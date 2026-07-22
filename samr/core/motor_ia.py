"""
MedGeminiEngine (stub) -- motor de IA clinica compartido por M2 y M3.

Es un stub deliberado: clasifica por reglas/palabras clave en vez de invocar
un modelo real, para poder demostrar el flujo completo end-to-end sin
depender de una API externa de IA. La interfaz (nombres de metodo, forma de
la respuesta) es la misma que usaria una integracion real, para que
reemplazarlo despues sea un cambio de implementacion, no de contrato.
"""
import random
import re

VERSION_MODELO = "med-gemini-stub-0.2"

SINTOMAS_CONOCIDOS = [
    # Críticos (9-10)
    (r"dolor\s+(en\s+el\s+)?pecho|duele\s+(el\s+)?pecho", "dolor en el pecho", 10),
    (r"dificultad\s+para\s+respirar|no\s+puedo\s+respirar|falta\s+el\s+aire", "dificultad para respirar", 10),
    (r"p[eé]rdida\s+de\s+conciencia|desmayo", "pérdida de conciencia", 9),
    (r"convulsi[oó]n(es)?", "convulsiones", 9),
    (r"sangrado\s+abundante", "sangrado abundante", 9),
    # Urgentes (5-6)
    (r"fiebre\s+alta", "fiebre alta", 6),
    (r"v[oó]mito\s+persistente", "vómito persistente", 6),
    (r"dolor\s+intenso|duele\s+mucho", "dolor intenso", 5),
    (r"mareo\s+fuerte", "mareo fuerte", 5),
    # Normales (1-3)
    (r"dolor\s+de\s+cabeza|duele\s+(la\s+)?cabeza", "dolor de cabeza", 3),
    (r"fiebre(?!\s+alta)", "fiebre", 3),
    (r"tos", "tos", 1),
    (r"n[aá]useas?", "náuseas", 2),
    (r"cansancio", "cansancio", 1),
    (r"dolor\s+muscular", "dolor muscular", 2),
    (r"congesti[oó]n\s+nasal", "congestión nasal", 1),
    (r"dolor\s+de\s+garganta", "dolor de garganta", 2),
    (r"mareo(s)?(?!\s+fuerte)", "mareo leve", 1),
    (r"diarrea", "diarrea", 2),
]

def clasificar_sintomas(texto_sintomas):
    """
    RF-05: clasifica la descripcion de sintomas del paciente y devuelve
    nivel de urgencia (escala Manchester 1-5) + explicacion XAI + nivel de confianza.
    """
    try:
        from core.motor_ia_llm import clasificar_sintomas_llm
        resultado_llm = clasificar_sintomas_llm(texto_sintomas)
        if resultado_llm:
            return resultado_llm
    except Exception:
        pass
    texto = (texto_sintomas or "").strip()
    
    if not texto:
        return {
            "nivel_urgencia": 5,
            "explicacion_xai": "No se recibió descripción de síntomas.",
            "confianza": 0.0,
            "sintomas_detectados": [],
            "version_modelo": VERSION_MODELO,
        }

    sintomas_detectados = []
    max_peso = 0
    
    for patron, etiqueta, peso in SINTOMAS_CONOCIDOS:
        if re.search(patron, texto, re.IGNORECASE):
            if etiqueta not in sintomas_detectados:
                sintomas_detectados.append(etiqueta)
                if peso > max_peso:
                    max_peso = peso

    if max_peso >= 9:
        nivel = 1
    elif max_peso >= 5:
        nivel = 2
    elif max_peso >= 3:
        nivel = 3
    elif max_peso >= 1:
        nivel = 4
    else:
        nivel = 5
        
    if sintomas_detectados:
        sintomas_str = " y ".join([", ".join(sintomas_detectados[:-1]), sintomas_detectados[-1]] if len(sintomas_detectados) > 1 else sintomas_detectados)
        if nivel == 1:
            explicacion = f"Se identificaron: {sintomas_str}. Esto requiere atención inmediata."
        elif nivel == 2:
            explicacion = f"Se identificaron: {sintomas_str}. Estos síntomas son urgentes y requieren atención pronta."
        elif nivel == 3:
            explicacion = f"Se identificaron: {sintomas_str}. Prioridad moderada."
        else:
            explicacion = f"Se identificaron: {sintomas_str}. La condición descrita no presenta signos de gravedad inminente."
        confianza = round(min(0.75 + len(sintomas_detectados) * 0.05, 0.99), 2)
    else:
        explicacion = f'No se reconocieron síntomas específicos en el texto: "{texto}". Se asigna prioridad normal (baja) por defecto.'
        confianza = 0.50

    return {
        "nivel_urgencia": nivel,
        "explicacion_xai": explicacion,
        "confianza": confianza,
        "sintomas_detectados": sintomas_detectados,
        "version_modelo": VERSION_MODELO,
    }

def responder_chat(mensajes_chat, mensaje_actual, turno):
    """
    RF-04: Chat conversacional para triaje.
    """
    try:
        from core.motor_ia_llm import responder_chat_llm
        resultado_llm = responder_chat_llm(mensajes_chat, mensaje_actual, turno)
        if resultado_llm:
            if resultado_llm.get("listo_para_clasificar"):
                textos = []
                for m in (mensajes_chat or []):
                    txt = getattr(m, "texto", m.get("texto") if isinstance(m, dict) else "")
                    if txt:
                        textos.append(txt)
                textos.append(mensaje_actual)
                texto_completo = " ".join(textos).strip()
                resultado_llm["resultado"] = clasificar_sintomas(texto_completo)
            return resultado_llm
    except Exception:
        pass

    textos = []
    for m in (mensajes_chat or []):
        txt = getattr(m, "texto", m.get("texto") if isinstance(m, dict) else "")
        if txt:
            textos.append(txt)
    textos.append(mensaje_actual)
    texto_completo = " ".join(textos).strip()
    resultado = clasificar_sintomas(texto_completo)
    
    critico = False
    for patron, etiqueta, peso in SINTOMAS_CONOCIDOS:
        if peso >= 9 and re.search(patron, texto_completo, re.IGNORECASE):
            critico = True
            break
            
    if critico or turno >= 2:
        return {
            "texto_respuesta": "Gracias por la información. Procedo a clasificar su estado...",
            "listo_para_clasificar": True,
            "resultado": resultado
        }
    else:
        if turno == 0:
            pregunta = "¿Desde cuándo presentas estos síntomas? ¿Han empeorado?"
        else:
            pregunta = "¿Algún otro detalle o molestia que debamos saber?"
        return {
            "texto_respuesta": pregunta,
            "listo_para_clasificar": False,
            "resultado": None
        }


def detectar_anomalia(tipo_signo, valor, rango_normal):
    """
    RF-10: analiza una lectura biometrica y determina si hay un patron
    precursor de evento critico, con explicacion XAI.
    """
    minimo, maximo = rango_normal
    fuera_rango = valor < minimo or valor > maximo
    if not fuera_rango:
        return None

    desviacion = abs(valor - (minimo if valor < minimo else maximo))
    critica = desviacion > (maximo - minimo) * 0.5
    nivel = "CRITICA" if critica else "ADVERTENCIA"
    explicacion = (
        "Lectura de {0} en {1}, fuera del rango normal ({2}-{3}). "
        "Desviacion {4} respecto al limite mas cercano.".format(
            tipo_signo, valor, minimo, maximo,
            "alta" if critica else "moderada",
        )
    )
    return {"nivel": nivel, "explicacion_xai": explicacion, "version_modelo": VERSION_MODELO}
