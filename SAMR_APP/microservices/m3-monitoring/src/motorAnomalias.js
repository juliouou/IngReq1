// Adaptador a Med-Gemini (stub deliberado, mismo patron que M2): detecta
// anomalias por umbral fijo en vez de un modelo predictivo real. Interfaz
// estable para poder reemplazar la implementacion despues sin tocar el
// contrato de /biometrics.
const VERSION_MODELO = "med-gemini-stub-0.1";

const RANGOS_NORMALES = {
  FC: [60, 100],
  SPO2: [95, 100],
  TA_SIS: [90, 130],
  TEMP: [36.1, 37.5],
};

function detectarAnomalia(tipo, valor) {
  const rango = RANGOS_NORMALES[tipo];
  if (!rango) return null;

  const [minimo, maximo] = rango;
  if (valor >= minimo && valor <= maximo) return null;

  const limite = valor < minimo ? minimo : maximo;
  const desviacion = Math.abs(valor - limite);
  const critica = desviacion > (maximo - minimo) * 0.5;

  return {
    nivel: critica ? "CRITICA" : "ADVERTENCIA",
    explanation: `Lectura de ${tipo} en ${valor}, fuera del rango normal (${minimo}-${maximo}).`,
    versionModelo: VERSION_MODELO,
  };
}

module.exports = { detectarAnomalia, RANGOS_NORMALES };
