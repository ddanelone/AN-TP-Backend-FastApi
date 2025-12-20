# services.tp1/inciso_1.py

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve
import math as mt
import io
import os
from scipy.fft import fft, fftfreq

fs = 173.61
cutoff = 40.0
NUM_TAPS = 301

ETAPAS = {
    0: 'Registro sano',
    1: 'Registro interictal',
    2: 'Registro convulsivo'
}

def cargar_senal(nombre_archivo):
    ruta = os.path.join("data", "tp1", nombre_archivo)
    with open(ruta, 'r') as f:
        return np.array([float(line.strip()) for line in f if line.strip()])

def filtro_pasa_bajos(data, cutoff, fs, num_taps=NUM_TAPS):
    fc = cutoff / (fs / 2)
    h = np.sinc(2 * fc * (np.arange(num_taps) - (num_taps - 1) / 2))
    h *= np.hamming(num_taps)
    h /= np.sum(h)
    return convolve(data, h, mode='same')

def generar_grafico_comparativo():
    # Cargar señales
    senales = [cargar_senal(f"Signal_{i}.txt") for i in range(1, 4)]
    t = np.arange(len(senales[0])) / fs
    senales_filtradas = [filtro_pasa_bajos(s, cutoff, fs) for s in senales]

    # Graficar comparativa
    fig, axs = plt.subplots(3, 1, figsize=(15, 8))
    for i in range(3):
        axs[i].plot(t, senales[i], label='Original', color='black', alpha=0.5, linewidth=1.0)
        axs[i].plot(t, senales_filtradas[i], label=f'Filtrada (Low-pass {mt.ceil(cutoff)} Hz)', color='tab:blue', linewidth=1.5)
        axs[i].set_title(f"Señal {i + 1} ({ETAPAS[i]}) - Comparativa")
        axs[i].set_xlabel("Tiempo [s]")
        axs[i].set_ylabel("Amplitud")
        axs[i].legend(loc="upper right")

    fig.tight_layout()

    # Guardar en buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def calcular_fft(senal, fs):
    n = len(senal)
    yf = fft(senal)
    xf = fftfreq(n, 1/fs)[:n//2]
    return xf, 2.0/n * np.abs(yf[0:n//2]) # type: ignore

def generar_grafico_fft_lineas():
    senales = [cargar_senal(f"Signal_{i}.txt") for i in range(1, 4)]
    senales_filtradas = [filtro_pasa_bajos(s, cutoff, fs) for s in senales]
    ffts = [calcular_fft(s, fs) for s in senales_filtradas]
    band_limits = [4, 8, 13, 30]

    fig, axs = plt.subplots(3, 1, figsize=(15, 8))
    for i, (xf, yf) in enumerate(ffts):
        mask = xf <= 40
        axs[i].plot(xf[mask], yf[mask])
        axs[i].set_title(f"Señal {i + 1} ({ETAPAS[i]}) - FFT")
        axs[i].set_xlabel("Frecuencia [Hz]")
        axs[i].set_ylabel("Magnitud [u.a.]")
        axs[i].grid(True)
        axs[i].set_xlim(-1, mt.ceil(cutoff))
        for limit in band_limits:
            axs[i].axvline(x=limit, color='red', linestyle='--', linewidth=1)

    fig.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def generar_grafico_fft_tallo():
    senales = [cargar_senal(f"Signal_{i}.txt") for i in range(1, 4)]
    senales_filtradas = [filtro_pasa_bajos(s, cutoff, fs) for s in senales]
    ffts = [calcular_fft(s, fs) for s in senales_filtradas]
    band_limits = [4, 8, 13, 30]

    fig, axs = plt.subplots(3, 1, figsize=(15, 8))
    for i, (xf, yf) in enumerate(ffts):
        mask = xf <= 40
        markerline, stemlines, baseline = axs[i].stem(xf[mask], yf[mask], linefmt='tab:blue', markerfmt=' ', basefmt=' ')
        plt.setp(stemlines, linewidth=1.5)
        axs[i].set_title(f"Señal {i + 1} ({ETAPAS[i]}) - FFT (Tallo)")
        axs[i].set_xlabel("Frecuencia [Hz]")
        axs[i].set_ylabel("Magnitud [u.a.]")
        axs[i].grid(True)
        axs[i].set_xlim(-1, mt.ceil(cutoff))
        for limit in band_limits:
            axs[i].axvline(x=limit, color='red', linestyle='--', linewidth=1)

    fig.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

EXPLICACION_FRECUENCIAS = """
🧠 Frecuencias características en señales EEG:

Durante el análisis de EEG, distintas bandas de frecuencia están asociadas a diferentes estados cerebrales. En el contexto de la epilepsia, estas bandas permiten distinguir entre un cerebro sano, un estado interictal (entre crisis) y una convulsión activa.

Bandas cerebrales típicas:

• Delta (0.5 – 4 Hz): asociada a sueño profundo. Puede aumentar en condiciones patológicas.\n
• Theta (4 – 8 Hz): típica de estados de somnolencia o meditación.\n
• Alfa (8 – 13 Hz): presente en reposo con ojos cerrados, típica de un cerebro sano.\n
• Beta (13 – 30 Hz): asociada a concentración o estrés. Suele reducirse en episodios convulsivos.\n
• Gamma (>30 Hz): involucrada en procesos cognitivos complejos.\n

En pacientes epilépticos se observa:\n

✔️ En etapa interictal: reducción en alfa y aumento de theta o delta.\n
✔️ Durante una convulsión: el EEG se vuelve caótico, con actividad abrupta en varias bandas, particularmente en la gama baja (delta y theta) y picos irregulares en otras.\n
✔️ La frecuencia de corte elegida (40 Hz) se basa en la observación de que las bandas cerebrales más relevantes para el diagnóstico y análisis de epilepsia se encuentran por debajo de este valor, permitiendo eliminar ruido de alta frecuencia que no aporta información diagnóstica.\n

🔍 Conclusión:
El análisis espectral permite identificar estas diferencias, y justificar el uso de un filtro pasa bajos con corte en 40 Hz, ya que concentra la mayoría de la actividad cerebral relevante en epilepsia.


"""

PROBLEMAS_INCISO_1 = """
📘 Resolución del TP1 - Inciso 1: Análisis de señales EEG

Este trabajo se enfocó en el análisis de tres señales EEG que representan distintas etapas del ciclo epiléptico: sano, interictal y convulsivo. El objetivo fue estudiar sus diferencias mediante procesamiento digital y análisis espectral.

🔹 Señales analizadas:
- **Señal 1:** registro sano
- **Señal 2:** registro interictal (entre crisis)
- **Señal 3:** registro durante convulsión

🔹 Filtro aplicado:
Se implementó un filtro pasa bajos ideal (FIR con ventana de Hamming) con frecuencia de corte en 40 Hz, para conservar las bandas cerebrales relevantes y eliminar ruido de alta frecuencia.

🔹 Gráficos generados:
1. **Gráfico 1 (/grafico1):** Comparación visual de señales crudas y filtradas en el dominio del tiempo.
2. **Gráfico 2 (/grafico2):** Espectros de frecuencia (FFT) de las señales, representados con líneas continuas. Se agregaron divisiones verticales para identificar bandas cerebrales: Delta, Theta, Alfa y Beta.
3. **Gráfico 3 (/grafico3):** Diagrama de tallo del espectro de frecuencia, útil para resaltar picos específicos.

🔍 Conclusión:
El análisis espectral permite distinguir claramente entre las etapas. En señales patológicas (interictal y convulsiva) se observa una mayor presencia de componentes en bandas bajas (Delta y Theta) y pérdida de regularidad en Alfa y Beta, respecto a la señal sana. Esto justifica el uso de un filtro pasa bajos y el análisis por transformada de Fourier como herramientas diagnósticas clave.
"""

def obtener_fs():
    return fs

def obtener_etapas():
    return ETAPAS

def cargar_senales_filtradas():
    senales = [cargar_senal(f"Signal_{i}.txt") for i in range(1, 4)]
    senales_filtradas = [filtro_pasa_bajos(s, cutoff, fs) for s in senales]
    return senales_filtradas

CONSIGNA = """
1. Investigar y detallar cuales son las frecuencias características que varían dependiendo de la etapa observadas
en un EEG de un paciente epiléptico y uno sano. Utilice un filtro pasa bajos para eliminar el ruido y enfocar
el análisis en las frecuencias más relevantes para la epilepsia. Determine una frecuencia de corte adecuada
y justifique su valor. Se pueden emplear librerias de filtros pre-programados en el lenguaje que utilice para
realizar el TP.
"""