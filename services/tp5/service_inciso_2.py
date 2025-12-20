# services/tp5/service_inciso_2.py
import io
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from .core import tp5_processor

# Configurar backend no interactivo para evitar errores de GUI en servidor
matplotlib.use('Agg')

CONSIGNA = r"""
**2. Modelo de la Dinámica de la Gota (EDO)**

Se modela la dinámica de *spreading* (esparcimiento) de la gota asumiendo que su centro de masa se comporta como un sistema masa-resorte-amortiguador. La ecuación diferencial ordinaria (EDO) de segundo orden que describe la altura $y(t)$ es:

$$ m \frac{d^2y}{dt^2} + c \frac{dy}{dt} + k(y - y_{eq}) = 0 $$

**Donde:**
* $m$: Masa de la gota [kg].
* $c$: Coeficiente de amortiguamiento viscoso [N·s/m].
* $k$: Constante de rigidez efectiva [N/m].
* $y_{eq}$: Altura de equilibrio [m].

**Objetivos:**
1.  **Resolver numéricamente** la EDO utilizando:
    * Método de **Taylor de Orden 3**.
    * Método de **Adams-Bashforth-Moulton (Predictor-Corrector) de Orden 4**.
2.  **Validar** los resultados comparando con una solución de referencia de alta precisión (Runge-Kutta 45).
3.  **Comparar** las soluciones numéricas con los datos experimentales obtenidos en el TP4, ajustando los parámetros $k$ y $c$ empíricamente.
"""

PROBLEMAS = r"""
### 🔍 Análisis de Resultados y Dificultades

**1. Ajuste de Parámetros ($k, c$)**
La principal dificultad radicó en encontrar valores de rigidez y amortiguamiento que ajustaran el modelo a la realidad física.
* Se observó que la frecuencia natural $\omega_n = \sqrt{k/m}$ determinaba el periodo de oscilación.
* El factor $\zeta = c / (2\sqrt{km})$ controlaba qué tan rápido decaía la oscilación.

**2. Comparación de Métodos Numéricos**
* **Taylor (Orden 3):** Requiere calcular derivadas analíticas ($y''', y''''$), lo cual es computacionalmente costoso si la EDO es compleja, aunque para este sistema lineal fue manejable.
* **Adams-Bashforth-Moulton (Orden 4):** Resultó ser muy eficiente. Al ser un método multipaso, reutiliza puntos anteriores, lo que reduce el costo computacional frente a RK4 para la misma precisión.
* **Estabilidad:** Ambos métodos se mantuvieron estables para el paso de tiempo utilizado ($\Delta t \approx 10^{-4}$ s).

**3. Datos Experimentales**
Fue necesario aplicar un **offset vertical** a los datos crudos del tracker para alinear el estado estacionario experimental con el $y_{eq}$ teórico ($0.13$ mm), ya que el cero experimental dependía de la calibración de la cámara.
"""

def get_console_output():
    """
    Genera un reporte en formato Markdown estilo 'Array/Vector' 
    para evitar problemas de renderizado de tablas.
    """
    # Trigger para asegurar que el procesador haya corrido
    data = tp5_processor.get_ode_data()
    
    # Datos base
    rk_y = data["rk"]["y"] * 1000 # a mm
    tay_y = data["tay"]["y"] * 1000
    abm_y = data["abm"]["y"] * 1000
    t_ms = data["rk"]["t"] * 1000

    # Interpoladores
    from scipy.interpolate import interp1d
    f_tay = interp1d(data["tay"]["t"]*1000, tay_y, fill_value="extrapolate")
    f_abm = interp1d(data["abm"]["t"]*1000, abm_y, fill_value="extrapolate")
    
    # Seleccionamos 6 puntos equidistantes para el muestreo
    puntos = 6
    tiempos_interes = np.linspace(t_ms[0], t_ms[-1], puntos)
    
    # Listas para guardar los strings formateados
    s_t, s_rk, s_tay, s_abm, s_err = [], [], [], [], []
    
    for t in tiempos_interes:
        # Interpolación
        idx = (np.abs(t_ms - t)).argmin()
        val_rk = rk_y[idx]
        val_tay = f_tay(t)
        val_abm = f_abm(t)
        
        # Cálculo error relativo
        err_rel = abs((val_tay - val_rk) / val_rk) * 100 if val_rk != 0 else 0.0
        
        # Formateo (fijamos ancho para que alineen visualmente aunque no sea tabla)
        s_t.append(f"{t:5.2f}")
        s_rk.append(f"{val_rk:6.4f}")
        s_tay.append(f"{val_tay:6.4f}")
        s_abm.append(f"{val_abm:6.4f}")
        s_err.append(f"{err_rel:5.2f}%")

    # Construcción de los "Vectores" visuales
    def armar_vector(lista):
        return "`[ " + " | ".join(lista) + " ]`"

    # Armado del reporte Markdown
    output = "### 📊 Muestreo de Resultados (Vectores de Estado)\n\n"
    
    output += "**⏱️ Tiempos de Muestreo [ms]:**\n"
    output += armar_vector(s_t) + "\n\n"
    
    output += "**🔹 Referencia (RK45) [mm]:**\n"
    output += armar_vector(s_rk) + "\n\n"
    
    output += "**🔸 Taylor Orden 3 [mm]:**\n"
    output += armar_vector(s_tay) + "\n\n"
    
    output += "**🔹 Adams-Bashforth-Moulton 4 [mm]:**\n"
    output += armar_vector(s_abm) + "\n\n"
    
    output += "---\n"
    output += "**⚠️ Error Relativo (Taylor vs RK45):**\n"
    output += armar_vector(s_err) + "\n\n"
    
    output += "> **Nota:** Los valores representan una selección de 6 instantes equidistantes de la simulación completa."
    
    return output

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
    # Convertimos yeq a mm para el gráfico
    yeq_mm = data["yeq"] * 1000
    ax.axhline(yeq_mm, color='orange', linestyle='-.', label=f'Equilibrio ({yeq_mm:.2f} mm)')
    
    ax.set_title(f"Dinámica Gota: Comparación Modelos vs Realidad")
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Posición [mm]")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Ajuste de límites inteligente basado en datos
    ax.set_xlim(0, max(rk["t"])*1000)
    # Un poco de margen vertical
    ymin = min(rk["y"])*1000
    ymax = max(rk["y"])*1000
    margin = (ymax - ymin) * 0.1
    ax.set_ylim(ymin - margin, ymax + margin)
    
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
    # Asumimos que la velocidad está en m/s, la pasamos a mm/s o la dejamos en m/s pero aclaramos
    # Para consistencia visual, pasemos posición a mm y velocidad a mm/s
    ax.plot(data["rk"]["y"]*1000, data["rk"]["v"]*1000, 'k-', alpha=0.6, lw=2, label="Ciclo Límite (RK45)")
    
    # Taylor (Comparación)
    ax.plot(data["tay"]["y"]*1000, data["tay"]["v"]*1000, 'r--', alpha=0.8, lw=1, label="Taylor 3")
    
    # Equilibrio
    yeq_mm = data["yeq"] * 1000
    ax.plot(yeq_mm, 0, 'bo', label="Punto Equilibrio")

    ax.set_xlabel("Posición y(t) [mm]")
    ax.set_ylabel("Velocidad v(t) [mm/s]")
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