import io
import matplotlib.pyplot as plt
import numpy as np
from .core import tp5_processor

CONSIGNA = """
1. Cálculo de Volumen y Área (Integración Numérica)
a) Ajustar el perfil de la gota.
b) Calcular Volumen y Área Superficial usando métodos de Trapecios y Simpson 1/3.
c) Analizar la convergencia y el error (Extrapolación de Richardson).
d) Comparar con el volumen de una esfera ideal.
"""

PROBLEMAS = """
**Desafíos en la Integración del Perfil:**
* **Ruido en el contorno:** Los métodos de derivada numérica (necesarios para el Área) son sensibles al ruido. El ajuste por Splines suaviza esto mejor que el Polinomio.
* **Simetría:** Se asume simetría de revolución. Las desviaciones reales de la gota introducen error sistemático.
* **Convergencia:** Simpson mostró un orden de convergencia superior ($O(h^4)$) comparado con Trapecios ($O(h^2)$), logrando menor error con la misma cantidad de puntos.
"""

def get_console_output():
    tp5_processor.get_integration_data() # Trigger
    return tp5_processor.console_output_1

def generar_grafico_volumen():
    data = tp5_processor.get_integration_data()
    t = data["t"]
    v = data["v"]
    v_ideal = data["v_ideal"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t, v, 'b-', label="Volumen Experimental (Integrado)")
    ax.axhline(v_ideal, color='r', linestyle='--', label=f"Volumen Ideal Esfera ({v_ideal} mm³)")
    
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Volumen [mm³]")
    ax.set_title("Comparación Volumen: Experimental vs Ideal")
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf
 
def generar_grafico_radio():
    data = tp5_processor.get_integration_data()
    t = data["t"]
    r = data["r_mm"]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t, r, 'm-', label="Radio de Contacto")
    
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Radio [mm]")
    ax.set_title("Evolución del Radio de Contacto (Expansión/Contracción)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf

def generar_grafico_perfil_80():
    """
    Genera un gráfico visualmente rico del perfil de la gota en el Frame 80.
    Muestra los puntos experimentales y la curva de ajuste que define el volumen.
    """
    data = tp5_processor.get_perfil_frame_80()
    if not data: return None
    
    y_raw = data["y_raw_um"]
    r_raw = data["r_raw_um"]
    y_fit = data["y_fit_um"]
    r_fit = data["r_fit_um"]
    
    fig, ax = plt.subplots(figsize=(7, 7))
    
    # 1. Puntos Experimentales (Scatter con transparencia)
    # Graficamos ambos lados (R y -R) para dar efecto de "gota completa"
    ax.scatter(r_raw, y_raw, s=10, color='gray', alpha=0.4, label='Borde Detectado (px)')
    ax.scatter(-r_raw, y_raw, s=10, color='gray', alpha=0.4)
    
    # 2. Ajuste Matemático (Línea sólida potente)
    ax.plot(r_fit, y_fit, 'b-', linewidth=2.5, label='Perfil Ajustado $R(y)$ (Spline)')
    ax.plot(-r_fit, y_fit, 'b-', linewidth=2.5)
    
    # 3. Relleno (Volumen de revolución visual)
    ax.fill_betweenx(y_fit, -r_fit, r_fit, color='blue', alpha=0.1, label='Volumen de Revolución')
    
    # 4. Eje de Simetría
    ax.axvline(0, color='k', linestyle='--', linewidth=1, alpha=0.5, label='Eje Simetría')
    
    # Decoración
    ax.set_title("Reconstrucción del Perfil de la Gota (Frame 80)", fontsize=14)
    ax.set_xlabel("Radio Radial $r$ [µm]", fontsize=12)
    ax.set_ylabel("Altura $y$ [µm]", fontsize=12)
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axis('equal') # Importante para que no se vea deformada
    
    # Ajustes finales
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100) # DPI 100 para buena calidad
    plt.close(fig)
    buf.seek(0)
    return buf