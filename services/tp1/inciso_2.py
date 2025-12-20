# services/tp1/inciso_2.py
import os
import io
import math as mt
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Configurar backend no interactivo para servidor
matplotlib.use('Agg')

# --- Constantes y Configuración ---
fs = 173.61  # Frecuencia de muestreo
CUTOFF = 40.0 # Hz para el filtro
DATA_PATH = "data/tp1/"  # <--- AJUSTA ESTA RUTA A DONDE TENGAS TUS ARCHIVOS .TXT

ETAPAS = {
    0: 'Registro sano',
    1: 'Registro interictal',
    2: 'Registro convulsivo'
}

# --- Textos del Inciso ---
EXPLICACION_INCISO_2 = """
🔬 Transformada de Fourier aplicada a señales EEG:

La Transformada de Fourier (FFT) permite descomponer una señal en sus componentes de frecuencia. En el contexto del EEG, esta herramienta es clave para identificar en qué bandas cerebrales se concentra la energía de la señal.

✅ Diferencias esperadas entre señales:
- **Sana:** espectro más regular y energía predominante en la banda alfa (8–13 Hz).
- **Interictal:** mayor dispersión espectral, presencia de componentes en theta (4–8 Hz) o incluso delta (0.5–4 Hz).
- **Convulsiva:** espectro caótico con actividad intensa y amplia distribución, pérdida de concentración en bandas típicas.

📈 Información adicional que ofrece la FFT:
- Permite identificar la **energía dominante** en cada banda.
- Muestra **activaciones anómalas** que no son visibles a simple vista en el dominio del tiempo.
- Facilita la detección de patrones repetitivos, armonías o picos inusuales.

💡 Mientras que en el tiempo solo vemos la amplitud en función de los segundos, la FFT revela el "contenido escondido" en el dominio de las frecuencias.
"""

PROBLEMAS_INCISO_2 = """
📘 Resolución del TP1 - Inciso 2: Análisis espectral mediante FFT

En este punto se reutilizaron las señales EEG previamente filtradas y se aplicó la Transformada Rápida de Fourier (FFT) a cada una. Los espectros obtenidos permitieron estudiar cómo varía el contenido frecuencial según el estado cerebral del paciente.

🔹 Señales utilizadas:
- **Señal 1 (sana):** espectro con picos definidos en alfa.
- **Señal 2 (interictal):** distribución espectral más difusa, sin picos bien definidos.
- **Señal 3 (convulsiva):** gran cantidad de componentes distribuidos en múltiples bandas.

🔍 Problemáticas abordadas:
- Se trabajó con señales discretas y de duración limitada, lo que implica resolución espectral restringida.
- Se aplicó una frecuencia de corte en 40 Hz para enfocarnos en las bandas clínicas más relevantes.
- Se compararon los resultados espectrales con las representaciones temporales para confirmar los patrones visuales.

✅ Conclusión:
La FFT aporta una dimensión adicional al análisis EEG, revelando información que el dominio del tiempo no permite observar directamente. Esto la convierte en una herramienta fundamental en el diagnóstico de epilepsia.
"""

CONSIGNA2 = """
2. Aplicar la transformada de Fourier a cada una de las señales. ¿Qué diferencias esperas encontrar en el
espectro de frecuencias de una señal sana frente a una señal interictal o durante la crisis epiléptica? ¿Qué
información adicional proporciona la FFT sobre la señal que no se puede obtener fácilmente en el dominio
del tiempo?
"""

# --- Funciones de Procesamiento ---

def cargar_senal(nombre_archivo):
    """Carga la señal desde un archivo de texto."""
    path = os.path.join(DATA_PATH, nombre_archivo)
    if not os.path.exists(path):
        # Fallback por si la ruta no es correcta, intenta en el directorio actual
        path = nombre_archivo 
        
    with open(path, 'r') as f:
        return np.array([float(line.strip()) for line in f if line.strip()])

def filtro_pasa_bajos(data, cutoff, fs, num_taps=301):
    """Filtro pasa bajos FIR usando ventana de Hamming."""
    fc = cutoff / (fs / 2)
    h = np.sinc(2 * fc * (np.arange(num_taps) - (num_taps - 1) / 2))
    h *= np.hamming(num_taps)
    h /= np.sum(h)
    return np.convolve(data, h, mode='same')

def generar_grafico_zoom_img():
    """
    Genera el gráfico de zoom (1 segundo) comparando señal original vs filtrada.
    Retorna los bytes de la imagen en formato PNG.
    """
    # 1. Cargar datos
    try:
        senales = [cargar_senal(f'Signal_{i}.txt') for i in range(1, 4)]
    except FileNotFoundError:
        # Retornar una imagen vacía o error si no hay datos (o manejar con excepción HTTP en router)
        return None

    t = np.arange(len(senales[0])) / fs
    
    # 2. Filtrar
    senales_filtradas = [filtro_pasa_bajos(s, CUTOFF, fs) for s in senales]

    # 3. Recortar ventana (t < 1 segundo)
    mask = t < 1
    t_ventana = t[mask]
    senales_ventana = [s[mask] for s in senales]
    filtradas_ventana = [s[mask] for s in senales_filtradas]

    # 4. Graficar
    fig = plt.figure(figsize=(15, 8))
    
    for i in range(3):
        etapa = ETAPAS[i]
        plt.subplot(3, 1, i + 1)

        # Desplazamiento visual para la original
        desplazamiento = 0.1 * np.std(senales_ventana[i])
        senal_original_desplazada = senales_ventana[i] + desplazamiento

        plt.plot(t_ventana, senal_original_desplazada, label='Original (desplazada)', color='gray', linestyle='--', linewidth=1)
        plt.plot(t_ventana, filtradas_ventana[i], label='Filtrada', color='blue', linewidth=2)
        
        # Diferencia
        diferencia = senal_original_desplazada - filtradas_ventana[i]
        plt.plot(t_ventana, diferencia, label='Diferencia', color='red', linestyle=':', linewidth=1)

        plt.title(f'Señal {i + 1} ({etapa}) - Zoom con Desplazamiento')
        plt.xlabel('Tiempo [s]')
        plt.ylabel('Amplitud')
        plt.legend(loc='upper right')

    plt.tight_layout()
    
    # 5. Guardar en buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig) # Importante cerrar la figura para liberar memoria
    buf.seek(0)
    
    return buf