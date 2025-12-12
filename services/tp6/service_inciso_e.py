# services/tp6/service_inciso_e.py
import numpy as np
import time
import matplotlib.pyplot as plt
from services.tp6.numerical import D0, simular_2D_lineal, save_plot_to_buffer
from services.tp6.core import processor

_cache_e = None

def get_consigna():
    return "e) Resuelva una gota elíptica (relación de ejes 2:1) usando la discretización completa en 2D y discuta las diferencias frente al caso circular."

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
    return """
    **Fundamentación y Conclusiones - Inciso E (Gota Elíptica):**
    
    1. **Fenómeno Físico:** Partimos de una elipse 2:1. La difusión es impulsada por el gradiente de concentración ($\nabla \theta$).
    
    2. **Mecanismo de Isotropización:**
       - El gradiente es más fuerte (la pendiente es más empinada) en el eje menor (el lado angosto de la elipse).
       - Por la Ley de Fick, el flujo difusivo es mayor donde el gradiente es mayor.
       
    3. **Conclusión:**
       - La gota se expande más rápido en su eje corto que en su eje largo.
       - Con el tiempo, la forma elíptica se va "redondeando". El sistema tiende naturalmente al equilibrio de menor energía, que es la forma circular.
    """