# services/tp6/service_inciso_f.py
import matplotlib.pyplot as plt
import numpy as np
from services.tp6.numerical import save_plot_to_buffer
from services.tp6.core import processor

def get_consigna():
    return r"""
**Inciso (f): Análisis de Costo Computacional y Estabilidad**

La elección de un método numérico siempre implica un compromiso entre precisión, estabilidad y tiempo de cómputo.

El esquema explícito utilizado (FTCS) es condicionalmente estable. Requiere cumplir la condición de Courant-Friedrichs-Lewy (CFL):

$$ \Delta t \le \frac{\Delta x^2}{2 \cdot n_{dim} \cdot D_{max}} $$

Donde $n_{dim}$ es la dimensión del problema (1 o 2).

---

**Consigna Final:**
Genere un reporte comparativo del **Tiempo de Ejecución** (Wall-clock time) para todos los incisos anteriores. Identifique qué factores (dimensionalidad vs. no-linealidad) impactan más severamente en el rendimiento del simulador.
"""

def get_console():
    times = processor.get_times()
    
    # Formateo de tabla
    w_inc = 12
    w_time = 18
    sep = "-" * (w_inc + w_time + 3)
    
    out = [
        "\n--- RESUMEN DE COSTO COMPUTACIONAL (Inciso F) ---",
        sep,
        f"{'--Inciso':<{w_inc}} | {'Tiempo (s)--':<{w_time}}",
        sep
    ]
    
    for k, v in times.items():
        if v == 0: val = "Pendiente"
        elif v < 0.001: val = "< 0.001 s"
        else: val = f"{v:.4f} s"
        
        out.append(f"{'Inciso '+k:<{w_inc}} | {val:<{w_time}}")
        
    out.append(sep)
    
    valid_times = {k: v for k, v in times.items() if v > 0}
    
    if valid_times:
        max_k = max(valid_times, key=valid_times.get)
        max_v = valid_times[max_k]
        out.append(f"\nEl inciso más costoso fue el {max_k} con {max_v:.2f} segundos.")
        if max_k == "B":
            out.append("Esto se debe a la alta no-linealidad (stiffness) del modelo Van Genuchten, que requiere un dt muy pequeño.")
        elif max_k in ["D", "E"]:
            out.append("Esto se debe al tamaño de la malla 2D y la cantidad de nodos.")
    else:
        out.append("\nNo hay datos de ejecución aún. Ejecuta los incisos anteriores.")
    
    return "\n".join(out)

def get_grafico_costos():
    times = processor.get_times()
    labels = list(times.keys())
    values = list(times.values())
    
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6']
    bars = ax.bar(labels, values, color=colors, edgecolor='black', alpha=0.7)
    
    ax.set_title("Comparativa de Costo Computacional por Inciso")
    ax.set_xlabel("Inciso del TP")
    ax.set_ylabel("Tiempo de Ejecución (segundos)")
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + (max(values)*0.01 if max(values)>0 else 0),
                    f'{height:.2f}s', ha='center', va='bottom', fontsize=9, fontweight='bold')
        else:
            ax.text(bar.get_x() + bar.get_width()/2., 0,
                    'N/A', ha='center', va='bottom', fontsize=8, color='gray')

    return save_plot_to_buffer(fig)
 
def get_explicacion():
    return r"""
### Análisis de Costo Computacional (Conclusiones)

**1. Dimensionalidad vs. Física:**
* **Inciso A (1D Lineal):** Instantáneo ($< 0.01s$).
* **Inciso C/D/E (2D Lineal):** Rápidos ($\approx 0.1s - 0.5s$). Aunque el número de nodos crece cuadráticamente ($N^2$), la estabilidad permite pasos de tiempo razonables.

**2. El Cuello de Botella (Inciso B):**
El caso 1D No Lineal (Van Genuchten) es, por lejos, el más costoso.
* **Razón:** La extrema no-linealidad ($D(\theta)$ variando en órdenes de magnitud) hace que el problema sea **rígido (stiff)**.
* Esto obliga al solver a tomar pasos de tiempo diminutos ($\Delta t \approx 10^{-5}s$) para no divergir, requiriendo cientos de miles de iteraciones para simular unos pocos segundos físicos.

**Conclusión General:**
Para estas escalas, la **complejidad constitutiva** (física no lineal) impacta mucho más en el tiempo de cómputo que la mera cantidad de nodos geométricos.
"""