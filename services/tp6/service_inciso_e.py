# services/tp6/service_inciso_e.py
import numpy as np
import time
import matplotlib.pyplot as plt
from services.tp6.numerical import D0, simular_2D_lineal, save_plot_to_buffer
from services.tp6.core import processor

_cache_e = None

def get_consigna():
    return r"""
**Inciso (e): Anisotropía Geométrica (Gota Elíptica)**

Cuando la condición inicial carece de simetría radial, no existen soluciones analíticas simples ni reducciones a 1D. Este caso evalúa la capacidad del solver 2D para manejar gradientes variables en distintas direcciones.

Físicamente, el flujo difusivo $\vec{J}$ es proporcional al gradiente de concentración:

$$ \vec{J} = -D \nabla \theta $$

En una elipse, el gradiente es más intenso en el eje menor (curvatura alta), lo que provoca una difusión más rápida en esa dirección, tendiendo a "redondear" la forma hacia un estado de mínima energía.

---

**Consigna:**
Resuelva la evolución de una **Gota Elíptica** (relación de ejes 2:1) utilizando la discretización completa en 2D y discuta cualitativamente el mecanismo de isotropización de la forma.
"""

def ic_elipse(X, Y, L):
    cx = L/2; cy = L/2; a = 0.6; b = 0.3
    eq = ((X-cx)/a)**2 + ((Y-cy)/b)**2
    return np.where(eq <= 1.0, 1.0, 0.0)

def _run_e():
    start = time.time()
    L = 2.0; h = 0.02; Nx = int(L/h)+1; T = 0.4
    # Unpack 9 valores
    _, _, _, _, th, _, _, _, _ = simular_2D_lineal(L, Nx, T, D0, lambda X,Y,L: ic_elipse(X,Y,L))
    elapsed = time.time() - start
    processor.record_time("E", elapsed)
    return {"th": th, "elap": elapsed, "N": Nx}

def _get_data():
    global _cache_e
    if _cache_e is None: _cache_e = _run_e()
    return _cache_e

def get_console():
    d = _get_data()
    return f"Ejecutando Inciso E...\n   Simulación 2D Elíptica completada en {d['elap']:.2f}s"

def get_grafico():
    d = _get_data()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_title("Inciso (e): Gota Elíptica 2D")
    im = ax.imshow(d['th'], origin='lower', cmap='viridis')
    fig.colorbar(im, ax=ax)
    return save_plot_to_buffer(fig)

def get_explicacion():
    return r"""
### Fundamentación y Conclusiones - Inciso E

**1. Fenómeno Físico:**
Partimos de una elipse con semieje mayor en $x$ y menor en $y$ (relación 2:1). La difusión es impulsada por el **gradiente de concentración** ($\nabla \theta$).

**2. Mecanismo de Isotropización:**
* El gradiente es mucho más fuerte (la pendiente es más empinada) a lo largo del **eje menor** de la elipse.
* Según la Ley de Fick ($J = -D \nabla \theta$), el flujo difusivo es mayor donde el gradiente es mayor.

**3. Conclusión:**
La gota se expande **más rápido en su eje corto** que en su eje largo.
* Con el tiempo, la forma elíptica se va "redondeando" espontáneamente.
* El sistema tiende naturalmente al estado de equilibrio de menor energía, que es la simetría circular (isotropía), borrando la memoria de su forma inicial.
"""