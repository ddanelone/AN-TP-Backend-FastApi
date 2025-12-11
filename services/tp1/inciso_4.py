from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt, welch
from scipy.integrate import trapezoid
import seaborn as sns
import math as mt

from services.tp1.inciso_1 import cargar_senales_filtradas, obtener_etapas, obtener_fs


EXPLICACION_INCISO_4 = """
📈 Análisis de autocorrelación en señales EEG

La función de **autocorrelación** mide cuán similar es una señal respecto de sí misma desplazada en el tiempo. Esto permite detectar patrones repetitivos y analizar la regularidad.

- En EEG, una señal **sana** suele tener patrones más rítmicos y organizados, generando autocorrelaciones que decaen lentamente.
- Una señal **interictal** muestra menor regularidad: la autocorrelación cae más rápido.
- En una señal **convulsiva**, dominan oscilaciones caóticas y de corta duración. La autocorrelación pierde forma estructurada.

👉 Para facilitar la comparación, se normalizó la autocorrelación (valor máximo igual a 1) y se representaron los primeros 2 segundos de retardo (lag), basados en la frecuencia crítica más baja: 0.5 Hz.
"""

PROBLEMAS_INCISO_4 = """
🧪 Resultados y reflexiones del inciso 4

🔹 Metodología:
- Se aplicó autocorrelación normalizada (`np.correlate`) a las señales filtradas.
- Se graficó la evolución de la autocorrelación en función del tiempo (retardo) para 2 segundos.

🔍 Observaciones:
- La señal sana conserva una estructura autocorrelativa con picos secundarios, indicando cierta periodicidad.
- La señal interictal tiene una rápida caída, reflejando actividad desincronizada.
- La señal convulsiva presenta una forma caótica: la autocorrelación es abrupta, sin periodicidad clara.

🎯 Conclusión:
El análisis de autocorrelación permite cuantificar la regularidad temporal de las señales. Es una herramienta eficaz para diferenciar entre actividad cerebral normal y patológica.
"""

def generar_grafico_autocorrelacion():
    senales = cargar_senales_filtradas()
    fs = obtener_fs()
    ETAPAS = obtener_etapas()

    def calcular_autocorrelacion(senal):
        autocorr = np.correlate(senal, senal, mode='full')
        autocorr = autocorr[len(autocorr)//2:] / np.max(autocorr)
        return autocorr

    autocorrelaciones = [calcular_autocorrelacion(s) for s in senales]
    t_autocorr = np.arange(len(autocorrelaciones[0])) / fs

    fig, axs = plt.subplots(3, 1, figsize=(15, 8))
    for i, ac in enumerate(autocorrelaciones):
        axs[i].plot(t_autocorr, ac)
        axs[i].set_xlim(0, 2)
        axs[i].set_title(f"Señal {i + 1} ({ETAPAS[i]}) - Autocorrelación")
        axs[i].set_xlabel("Retardo [s]")
        axs[i].set_ylabel("Correlación normalizada")

    fig.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return buffer

def generar_grafico_potencias_por_banda(potencias, ETAPAS):
    from scipy.integrate import trapezoid

    bandas = {
        'Delta (0.5-4 Hz)': (0.5, 4),
        'Theta (4-8 Hz)': (4, 8),
        'Alpha (8-13 Hz)': (8, 13),
        'Beta (13-30 Hz)': (13, 30),
        'Gamma (30-50 Hz)': (30, 50)
    }
    nombres_bandas = list(bandas.keys())

    potencias_bandas = []
    for f, Pxx in potencias:
        total = trapezoid(Pxx, f)
        potencias_por_senal = []
        for low, high in bandas.values():
            mask = (f >= low) & (f <= high)
            potencia = trapezoid(Pxx[mask], f[mask])
            porcentaje = (potencia / total) * 100
            potencias_por_senal.append(porcentaje)
        potencias_bandas.append(potencias_por_senal)

    potencias_bandas = np.array(potencias_bandas)
    x = np.arange(len(nombres_bandas))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    for i in range(len(ETAPAS)):
        ax.bar(x + i * width - width, potencias_bandas[i], width, label=f"Señal {i+1}")

    ax.set_xticks(x)
    ax.set_xticklabels(nombres_bandas)
    ax.set_ylabel("Potencia relativa [%]")
    ax.set_title("Distribución de Potencia por Bandas de Frecuencia")
    ax.legend()
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return buffer

def generar_resumen_analisis_bandas(potencias, ETAPAS):
    from scipy.integrate import trapezoid

    bandas = {
        'Delta (0.5-4 Hz)': (0.5, 4),
        'Theta (4-8 Hz)': (4, 8),
        'Alpha (8-13 Hz)': (8, 13), 
        'Beta (13-30 Hz)': (13, 30),
        'Gamma (30-50 Hz)': (30, 50)
    }

    resumen = ""
    for i, (f, Pxx) in enumerate(potencias):
        resumen += f"🔍 Análisis de bandas para Señal {i+1} ({ETAPAS[i]}):\n"
        total = trapezoid(Pxx, f)
        for nombre, (low, high) in bandas.items():
            mask = (f >= low) & (f <= high)
            potencia = trapezoid(Pxx[mask], f[mask])
            porcentaje = (potencia / total) * 100
            resumen += f"- {nombre}: {potencia:.4f} ({porcentaje:.2f}%)\n"
        resumen += "\n"
    return resumen

CONSIGNA4 = """
4. La autocorrelación muestra la similitud entre la señal y una versión desplazada de sí misma. Esto ayuda a
identificar patrones repetitivos y las diferencias de regularidad entre las señales. Calcular la autocorrelación
para cada señal y observar la estructura temporal de las mismas. ¿Qué diferencias espera encontrar en la
autocorrelación de las tres señales? ¿Cómo interpretaría los resultados de la autocorrelación en términos
de regularidad o irregularidad en las señales de EEG?
"""