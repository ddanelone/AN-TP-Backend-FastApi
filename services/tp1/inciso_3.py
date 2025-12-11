import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from io import BytesIO
import math as mt

from services.tp1.inciso_1 import cargar_senales_filtradas, obtener_fs, obtener_etapas

# Definición de bandas cerebrales
BANDAS = {
    "Delta": (0.5, 4),
    "Theta": (4, 8),
    "Alfa": (8, 13),
    "Beta": (13, 30)
}

# Cálculo de potencia espectral por banda
def calcular_potencia_bandas(senal, fs):
    n = len(senal)
    yf = np.abs(fft(senal))**2  # type: ignore
    xf = fftfreq(n, 1/fs)
    
    potencias = {}
    for banda, (low, high) in BANDAS.items():
        indices = np.where((xf >= low) & (xf <= high))
        potencias[banda] = np.sum(yf[indices])
    return potencias

# Cálculo para cada señal
senales_filtradas = cargar_senales_filtradas()
fs = obtener_fs()
ETAPAS = obtener_etapas()

potencias_banda = [calcular_potencia_bandas(s, fs) for s in senales_filtradas]

# Gráfico de barras comparativo
def generar_grafico_potencia_barras():
    etapas = list(ETAPAS.values())
    bandas = list(BANDAS.keys())
    
    data = np.array([[potencias[b] for b in bandas] for potencias in potencias_banda])

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(bandas))
    width = 0.25

    for i in range(len(etapas)):
        ax.bar(x + i * width, data[i], width, label=etapas[i])

    ax.set_ylabel("Potencia (u.a.)")
    ax.set_xlabel("Bandas cerebrales")
    ax.set_title("Potencia espectral por banda y etapa EEG")
    ax.set_xticks(x + width)
    ax.set_xticklabels(bandas)
    ax.legend()

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    return buffer

# Gráfico de líneas
def generar_grafico_potencia_lineas():
    etapas = list(ETAPAS.values())
    bandas = list(BANDAS.keys())
    
    x = np.arange(len(bandas))
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for i, etapa in enumerate(etapas):
        y = [potencias_banda[i][b] for b in bandas]
        ax.plot(bandas, y, marker="o", label=etapa)
    
    ax.set_ylabel("Potencia (u.a.)")
    ax.set_xlabel("Bandas cerebrales")
    ax.set_title("Potencia espectral por banda (curvas)")
    ax.grid(True)
    ax.legend()

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    return buffer

# Texto de explicación
EXPLICACION_INCISO_3 = """
⚡ Análisis de potencia espectral por banda en señales EEG

Cada señal EEG contiene componentes de frecuencia asociadas a bandas cerebrales específicas. Calcular la **potencia espectral** permite estimar cuánta energía hay concentrada en cada banda.

Bandas típicas:

- Delta (0.5–4 Hz): sueño profundo, patologías.
- Theta (4–8 Hz): somnolencia, actividad anormal en interictal.
- Alfa (8–13 Hz): reposo, cerebro sano.
- Beta (13–30 Hz): actividad consciente, atención.

✅ Interpretación:
- Señal sana muestra mayor potencia en alfa y beta.
- Señal interictal: aumento en theta, baja en alfa.
- Señal convulsiva: actividad intensa en delta/theta.

Esta técnica complementa el análisis espectral (FFT) al cuantificar la energía de forma agregada por banda.
"""

PROBLEMAS_INCISO_3 = """
📄 Resolución del TP1 - Inciso 3: Potencia espectral por bandas cerebrales

Inicialmente se aplicó incorrectamente el método de Welch (densidad espectral), cuando la consigna pedía estimar la **potencia espectral directa**. Esta fue luego corregida usando la Transformada de Fourier y sumando los módulos al cuadrado por banda.

🔹 Señales procesadas:
- Señales filtradas con cutoff en 40 Hz, usando un filtro FIR.

🔹 Resultados observados:
- Se verificó que las señales patológicas concentran más energía en bandas bajas (delta, theta).
- Se perdió la dominancia de alfa y beta en estados convulsivos.

🔍 Conclusión:
La potencia espectral es una herramienta útil para cuantificar actividad cerebral, y permite correlacionar energía por banda con el estado clínico del paciente.
"""

CONSIGNA3 = """
3. La potencia espectral de una señal puede ser calculada para observar la energía contenida en cada banda
de frecuencia. ¿Qué interpretacion se puede hacer sobre la potencia en diferentes bandas de frecuencia, y
cómo esa interpretacion se correlaciona con los patrones de actividad cerebral esperados para cada etapa
de la epilepsia?
"""