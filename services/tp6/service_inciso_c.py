# services/tp6/service_inciso_c.py
import numpy as np
import time
import matplotlib.pyplot as plt
from services.tp6.numerical import D0, simular_2D_lineal, save_plot_to_buffer
from services.tp6.core import processor

_cache_c = None

def get_consigna():
    return r"""
**Inciso (c): Difusión en 2D y Análisis de Convergencia**

Extendemos el problema a dos dimensiones espaciales. La ecuación de difusión lineal isotrópica se convierte en:

$$ \frac{\partial\theta}{\partial t} = D_0 \left( \frac{\partial^2\theta}{\partial x^2} + \frac{\partial^2\theta}{\partial y^2} \right) $$

Para validar solvers multidimensionales, es crucial analizar el orden de convergencia del error numérico al refinar la malla (disminuir $\Delta x$).

---

**Consigna:**

Implemente el esquema de diferencias finitas en un dominio cuadrado 2D. Realice una **Prueba de Convergencia de Malla**:

1. Calcule el error global usando la **Norma $L^2$** contra una solución analítica de variables separables:
   $$ ||E||_{L^2} = \sqrt{ \sum ( \theta_{num} - \theta_{exacta} )^2 \Delta x \Delta y } $$
2. Demuestre que el método posee convergencia cuadrática ($Error \propto \Delta x^2$).
"""

def _run_c():
    start_time = time.time()
    N_values = [11, 21, 31, 41]
    dx_list = []
    errors_list = []
    L = 1.0; T = 0.2
    
    ic = lambda X, Y, L: np.sin(np.pi*X/L)*np.sin(np.pi*Y/L)
    
    logs = []
    
    for N in N_values:
        dx = L/(N-1)
        # Desempaquetado correcto de 9 valores
        _, _, X, Y, th_num, T_real, dt, Nt, alpha = simular_2D_lineal(L, N, T, D0, ic)
        
        th_ana = np.exp(-2*D0*(np.pi/L)**2 * T_real) * np.sin(np.pi*X/L) * np.sin(np.pi*Y/L)
        l2 = np.sqrt(np.sum((th_num - th_ana)**2) * dx * dx)
        
        dx_list.append(dx); errors_list.append(l2)
        logs.append({"N":N, "dx":dx, "dt":dt, "Nt":Nt, "a":alpha, "err":l2})
        
    elapsed = time.time() - start_time
    processor.record_time("C", elapsed)
    
    return {"dx": dx_list, "err": errors_list, "logs": logs, "elapsed": elapsed}

def _get_data():
    global _cache_c
    if _cache_c is None: _cache_c = _run_c()
    return _cache_c

def get_console():
    """
    Genera un reporte en formato Markdown estilo vectorial 
    para analizar la convergencia de malla en FDM 2D.
    """
    d = _get_data()
    logs = d["logs"]

    # 1. Preparamos las listas de datos formateados
    #    (Extraemos columnas verticales a filas horizontales)
    
    list_N = [str(r['N']) for r in logs]
    
    # Notación científica para valores muy chicos
    list_dx = [f"{r['dx']:.2e}" for r in logs]
    list_dt = [f"{r['dt']:.2e}" for r in logs]
    list_err = [f"{r['err']:.2e}" for r in logs]
    
    # 2. Calculamos Ratios y Diagnóstico
    list_ratios = []
    list_status = []
    prev_err = None

    for r in logs:
        current_err = r["err"]
        
        if prev_err is None:
            # Nivel base (no hay con qué comparar)
            list_ratios.append(" — ")
            list_status.append("🔹 Base")
        else:
            ratio = prev_err / current_err
            list_ratios.append(f"{ratio:.2f}")
            
            # Lógica de semáforo según convergencia esperada (orden 2 -> ratio ~4)
            if ratio > 3.5:
                list_status.append("✅ Opt")  # Convergencia cuadrática
            elif ratio > 2.0:
                list_status.append("⚠️ Sub")  # Convergencia lenta
            else:
                list_status.append("❌ Baja") # Problemas
        
        prev_err = current_err

    # 3. Función helper para armar el "vector" visual
    def armar_vector(items):
        return "`[ " + " | ".join(items) + " ]`"

    # 4. Construcción del Reporte Markdown
    out = "### 🏗️ Convergencia de Malla (FDM 2D)\n\n"
    
    out += "**📏 Resolución de Malla ($N$):**\n"
    out += armar_vector(list_N) + "\n\n"
    
    out += "**📐 Espaciado Espacial ($dx$) [m]:**\n"
    out += armar_vector(list_dx) + "\n\n"
    
    out += "**⏱️ Paso Temporal ($dt$) [s]:**\n"
    out += armar_vector(list_dt) + "\n\n"
    
    out += "**📉 Error Global L2:**\n"
    out += armar_vector(list_err) + "\n\n"
    
    out += "---\n"
    
    out += "**🔄 Ratio de Convergencia (Esperado $\\approx 4.0$):**\n"
    out += armar_vector(list_ratios) + "\n\n"
    
    out += "**🧐 Diagnóstico:**\n"
    out += armar_vector(list_status) + "\n\n"
    
    out += f"> **Tiempo Total de Simulación:** {d['elapsed']:.2f} s"
    
    return out

def get_grafico_error():
    d = _get_data()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(r"Inciso (c): Prueba de Convergencia FDM 2D (Error $L^2$)")
    ax.plot(d['dx'], d['err'], 'bo-', label='Error L2 Numérico')
    
    C = d['err'][0] / (d['dx'][0]**2)
    dx_fit = np.array(d['dx'])
    ax.plot(dx_fit, C*(dx_fit**2), 'r--', label=r"Referencia $O(h^2)$")
    
    ax.set_xlabel("dx"); ax.set_ylabel("Error L2")
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.legend(); ax.grid(True, which="both", ls="--")
    ax.invert_xaxis()
    return save_plot_to_buffer(fig)
 
def get_explicacion():
    return r"""
### Fundamentación y Conclusiones - Inciso C

**1. Análisis de Estabilidad (CFL 2D):**
Al trabajar en 2D, la energía fluye en dos direcciones simultáneamente. La restricción de estabilidad es más estricta:
$$ \alpha = \frac{D \Delta t}{\Delta x^2} \le 0.25 $$

**2. Prueba de Convergencia:**
El objetivo es validar matemáticamente el código. Al graficar el **Error Global $L^2$** en escala logarítmica contra el espaciado $\Delta x$, obtenemos una recta.

* **Pendiente observada:** La pendiente de la curva azul es $m \approx 2$.
* **Significado:** Esto confirma que el método tiene un orden de error $O(\Delta x^2)$.
$$ ||E||_{L^2} \approx C \cdot (\Delta x)^2 $$

**3. Interpretación Práctica:**
La convergencia cuadrática implica que **duplicar la resolución de la malla** (ej. pasar de $N=20$ a $N=40$) reduce el error numérico aproximadamente **4 veces**. Esto se evidencia en la tabla de consola (columna *Ratio*).
"""