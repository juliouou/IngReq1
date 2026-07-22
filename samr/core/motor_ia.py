"""
MedGeminiEngine (stub) -- motor de IA clinica compartido por M2 y M3.

Es un stub deliberado: clasifica por reglas/palabras clave en vez de invocar
un modelo real, para poder demostrar el flujo completo end-to-end sin
depender de una API externa de IA. La interfaz (nombres de metodo, forma de
la respuesta) es la misma que usaria una integracion real, para que
reemplazarlo despues sea un cambio de implementacion, no de contrato.
"""
import random

PALABRAS_CRITICAS = (
    "dolor en el pecho", "dificultad para respirar", "no puedo respirar",
    "desmayo", "convulsion", "sangrado abundante", "perdida de conciencia",
)
PALABRAS_URGENTES = (
    "fiebre alta", "vomito persistente", "dolor intenso", "mareo fuerte",
)

VERSION_MODELO = "med-gemini-stub-0.1"


def clasificar_sintomas(texto_sintomas):
    """
    RF-05: clasifica la descripcion de sintomas del paciente y devuelve
    nivel de urgencia (escala Manchester 1-5, igual que NivelUrgencia del
    modelo triaje) + explicacion XAI + nivel de confianza.
    """
    texto = (texto_sintomas or "").lower()

    if any(p in texto for p in PALABRAS_CRITICAS):
        nivel, razon = 1, "se detectaron signos de posible emergencia vital"
    elif any(p in texto for p in PALABRAS_URGENTES):
        nivel, razon = 2, "se detectaron sintomas que requieren atencion pronta"
    elif len(texto) > 0:
        nivel, razon = 4, "los sintomas descritos no indican urgencia inmediata"
    else:
        nivel, razon = 4, "sin sintomas suficientes para clasificar; se asigna prioridad normal"

    confianza = round(random.uniform(0.82, 0.97), 2)
    explicacion = (
        "Clasificacion nivel {0}/5: {1}. Basado en el analisis del texto "
        "reportado por el paciente.".format(nivel, razon)
    )
    return {
        "nivel_urgencia": nivel,
        "explicacion_xai": explicacion,
        "confianza": confianza,
        "version_modelo": VERSION_MODELO,
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
