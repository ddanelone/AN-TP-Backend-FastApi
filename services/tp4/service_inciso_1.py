import matplotlib.pyplot as plt
import io
import cv2
import numpy as np
from .core import processor

# Textos
CONSIGNA = """
1) Procesamiento de imágenes y extracción de contornos
Se proveen una serie de imágenes de una gota cayendo sobre un sustrato.
Escala: 4.13 um/px. Velocidad: 20538 fps.

a) Procesar las imágenes para extraer el contorno de cada gota y ajustar la posición vertical para que
la base, en el punto donde toca el sustrato, coincida con y=0. Aplicar técnicas de segmentación.
Explicar brevemente.

b) Graficar la posición del centro de las gotas en función del tiempo.
"""

EXPLICACION = """
🔹 Procesamiento de Imágenes Realizado:

1. Detección del Sustrato:
   Se utilizó un algoritmo basado en Transformada de Hough y proyección de bordes (Canny) para encontrar la línea horizontal del sustrato (y0). Esto es crucial para establecer el sistema de referencia y=0.

2. Segmentación (Otsu + Morfología):
   - Se recorta la imagen por encima del sustrato para eliminar reflejos.
   - Se aplica desenfoque Gaussiano (5x5) para reducir ruido.
   - Se utiliza umbralización de Otsu (adaptativa) para separar la gota del fondo.
   - Se aplica una operación morfológica de Cierre (Closing) para rellenar huecos dentro de la gota.

3. Extracción de Contornos:
   Se utiliza `cv2.findContours` sobre la máscara binaria para obtener el borde preciso de la gota.

4. Cálculo de Centroide:
   Se utilizan los Momentos de la imagen (m00, m10, m01) sobre el área segmentada para hallar el centro de masa con precisión sub-píxel.
"""

def obtener_logs():
    processor.get_data()
    return processor.get_logs()

def generar_grafico_procesamiento():
    """Genera imagen comparativa: Original con corte vs Segmentada."""
    vis_data = processor.get_visualization_frame()
    if not vis_data: return None

    img = vis_data["original"]
    cont = vis_data["contorno"]
    cx, cy = vis_data["cx"], vis_data["cy"]
    y_sust = vis_data["y_sustrato"]
    
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    
    # 1. Imagen Original marcando el corte
    axs[0].imshow(img, cmap="gray")
    # Dibujamos la linea donde CORTAMOS la imagen
    axs[0].axhline(y_sust, color="r", linestyle="--", linewidth=2, label="Línea de Corte (Sustrato)")
    axs[0].set_title(f"Imagen Original (Frame Ejemplo)\nCorte en Y={y_sust}")
    axs[0].legend(loc='upper right')
    
    # 2. Resultado de la segmentación (Ya recortada)
    # Nota: 'binaria' y 'contorno' ya están en coordenadas recortadas (0 a y_sustrato)
    axs[1].imshow(vis_data["binaria"], cmap="gray")
    axs[1].plot(cont[:, 0], cont[:, 1], color="yellow", linewidth=2, label="Borde Gota")
    axs[1].scatter([cx], [cy], color="red", marker="x", s=100, label="Centro de Masa")
    axs[1].set_title("Gota Aislada (Sin Reflejo)")
    axs[1].legend()

    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def generar_grafico_trayectoria_vertical():
    """Grafica Y_centro vs Tiempo."""
    df = processor.get_data()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    y_um = df["cy_m"] * 1e6
    t_ms = df["t_ms"]
    
    ax.plot(t_ms, y_um, 'o-', markersize=3, color='tab:blue', label="Altura CM (Y)")
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Altura Y [µm]")
    ax.set_title("Posición Vertical del Centro de Masa")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def generar_grafico_posicion_horizontal():
    """Grafica X_centro vs Tiempo."""
    df = processor.get_data()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # X en micrones
    x_um = df["cx_m"] * 1e6
    t_ms = df["t_ms"]
    
    # Usamos un rango dinámico pequeño si la gota no se mueve mucho lateralmente
    ax.plot(t_ms, x_um, 's-', markersize=3, color='tab:green', label="Posición Horizontal (X)")
    
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Posición X [µm]")
    ax.set_title("Desplazamiento Horizontal del Centro de Masa")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def obtener_salida_consola():
    """Genera el texto formateado para la consola del Inciso 1."""
    df = processor.get_data()
    total_frames = len(df)
    t_total = df["t_ms"].iloc[-1]
    
    return f"""
--- RESUMEN DE PROCESAMIENTO DE IMÁGENES ---

> Total de Frames Procesados: {total_frames}
> Duración del evento: {t_total:.2f} ms
> Resolución Espacial: 4.13 µm/px
> Velocidad de Captura: 20538 fps

--- DETALLES DEL PROCESO ---
> Sustrato detectado y ajustado dinámicamente.
> Reflejos eliminados mediante recorte adaptativo.
> Segmentación por Otsu + Operaciones Morfológicas.

--- ESTAT DE TRAYECTORIA ---
> Desplazamiento vertical máximo (rebote): {df['cy_m'].max()*1e6:.2f} µm
> Posición final estable (aprox): {df['cy_m'].iloc[-10:].mean()*1e6:.2f} µm
""" 