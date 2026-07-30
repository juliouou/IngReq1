// Adaptador a Med-Gemini (stub deliberado): clasifica por palabras clave en
// vez de invocar un modelo real, para poder demostrar el flujo end-to-end
// sin depender de una API externa. La forma de la respuesta (nivel +
// explanation obligatoria) es la misma que usaria la integracion real, asi
// que reemplazar esto despues es un cambio de implementacion, no de
// contrato (ver shared/contracts/openapi/med-gemini-adapter.yaml).
const VERSION_MODELO = "med-gemini-stub-0.1";

const PALABRAS_CRITICAS = [
  "dolor en el pecho",
  "dolor toracico",
  "dificultad para respirar",
  "no puedo respirar",
  "desmayo",
  "convulsion",
  "sangrado abundante",
  "perdida de conciencia",
];
const PALABRAS_URGENTES = ["fiebre alta", "vomito persistente", "dolor intenso", "mareo fuerte"];

const NIVEL_A_PRIORIDAD = {
  1: { prioridad: "Alta", tiempoEstimado: "< 15 min" },
  2: { prioridad: "Alta", tiempoEstimado: "< 20 min" },
  3: { prioridad: "Moderada", tiempoEstimado: "30 min" },
  4: { prioridad: "Baja", tiempoEstimado: "60 min" },
  5: { prioridad: "Baja", tiempoEstimado: "90 min" },
};

function clasificarSintomas(textoSintomas, tipo) {
  const texto = (textoSintomas || "").toLowerCase();
  let nivel;
  let razon;

  if (tipo === "alerta_iot") {
    nivel = 1;
    razon = "alerta generada por un dispositivo IoT: se trata como emergencia hasta revision medica";
  } else if (PALABRAS_CRITICAS.some((p) => texto.includes(p))) {
    nivel = 1;
    razon = "se detectaron posibles signos de emergencia vital";
  } else if (PALABRAS_URGENTES.some((p) => texto.includes(p))) {
    nivel = 3;
    razon = "se detectaron sintomas que requieren atencion pronta";
  } else if (texto.length > 0) {
    nivel = 4;
    razon = "los sintomas descritos no indican urgencia inmediata";
  } else {
    nivel = 4;
    razon = "sin sintomas suficientes para clasificar; se asigna prioridad normal";
  }

  const sintomasDetectados = [...PALABRAS_CRITICAS, ...PALABRAS_URGENTES].filter((p) =>
    texto.includes(p)
  );

  return {
    nivel,
    ...NIVEL_A_PRIORIDAD[nivel],
    explanation: `Clasificacion nivel ${nivel}/5: ${razon}.`,
    sintomasDetectados,
    versionModelo: VERSION_MODELO,
  };
}

module.exports = { clasificarSintomas, VERSION_MODELO };
