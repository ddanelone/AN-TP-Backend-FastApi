import io
import matplotlib.pyplot as plt
import numpy as np
from .core import tp5_processor

CONSIGNA = """
2. Modelo de la Dinámica de la Gota (EDO)
Se resuelve la EDO de segundo orden que describe la altura del centro de masa:
$m y'' + c y' + k(y - y_{eq}) = 0$

Objetivos:
* Modelar el sistema masa-resorte-amortiguador.
* Resolver numéricamente usando Taylor (Orden 3) y Adams-Bashforth-Moulton (Orden 4).
* Comparar con datos experimentales y validar con RK45.
"""

PROBLEMAS = """
**Análisis del Modelo Dinámico:**
* **Alineación:** Fue necesario aplicar un desplazamiento vertical (offset) a los datos experimentales para que el punto de equilibrio coincida con $y_{eq}$ del modelo (0.13 mm).
* **Rigidez ($k$) y Amortiguamiento ($c$):** Se ajustaron empíricamente para capturar la frecuencia de oscilación y la tasa de decaimiento observada.
* **Estabilidad:** El método ABM4 (Predictor-Corrector) mostró excelente estabilidad y precisión, comparable a RK45, ideal para este tipo de oscilaciones amortiguadas.
"""

def get_console_output():
    tp5_processor.get_ode_data() # Trigger
    return tp5_processor.console_output_2

def generar_grafico_final():
    data = tp5_processor.get_ode_data()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 1. Modelo Referencia
    rk = data["rk"]
    ax.plot(rk["t"]*1000, rk["y"]*1000, 'k-', linewidth=2, label='Modelo Teórico (RK45)')
    
    # 2. Métodos Numéricos
    tay = data["tay"]
    abm = data["abm"]
    ax.plot(tay["t"]*1000, tay["y"]*1000, 'r--', linewidth=1.5, label='Taylor Orden 3')
    ax.plot(abm["t"]*1000, abm["y"]*1000, 'b:', linewidth=1.5, label='ABM Orden 4')
    
    # 3. Experimental
    exp = data["exp"]
    ax.plot(exp["t"]*1000, exp["y"]*1000, 'go', markersize=5, alpha=0.6, label='Datos Exp. (Alineados)')
    
    # 4. Equilibrio
    ax.axhline(data["yeq"], color='orange', linestyle='-.', label=f'Equilibrio ({data["yeq"]} mm)')
    
    ax.set_title(f"Dinámica Gota: Comparación Modelos vs Realidad")
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Posición [mm]")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 0.45)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf
 
def generar_grafico_fase():
    """Grafica el Espacio de Fase (Velocidad vs Posición)."""
    data = tp5_processor.get_ode_data()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # RK45 (Referencia)
    ax.plot(data["rk"]["y"]*1000, data["rk"]["v"], 'k-', alpha=0.6, lw=2, label="Ciclo Límite (RK45)")
    
    # Taylor (Comparación)
    ax.plot(data["tay"]["y"]*1000, data["tay"]["v"], 'r--', alpha=0.8, lw=1, label="Taylor 3")
    
    # Equilibrio
    yeq_mm = data["yeq"] * 1000
    ax.plot(yeq_mm, 0, 'bo', label="Punto Equilibrio")

    ax.set_xlabel("Posición y(t) [mm]")
    ax.set_ylabel("Velocidad v(t) [m/s]")
    ax.set_title("Retrato de Fase: Dinámica del Rebote")
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf

def generar_grafico_error():
    """Grafica el Error absoluto de los métodos vs RK45 a lo largo del tiempo."""
    data = tp5_processor.get_ode_data()
    
    # Interpolamos para restar en los mismos tiempos
    from scipy.interpolate import interp1d
    t_rk = data["rk"]["t"]
    y_rk = data["rk"]["y"]
    
    f_tay = interp1d(data["tay"]["t"], data["tay"]["y"], fill_value="extrapolate")
    f_abm = interp1d(data["abm"]["t"], data["abm"]["y"], fill_value="extrapolate")
    
    error_tay = np.abs(f_tay(t_rk) - y_rk)
    error_abm = np.abs(f_abm(t_rk) - y_rk)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogy(t_rk*1000, error_tay, 'r-', label="|Taylor - RK45|")
    ax.semilogy(t_rk*1000, error_abm, 'b--', label="|ABM4 - RK45|")
    
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Error Absoluto [m] (Log)")
    ax.set_title("Evolución del Error Numérico")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf