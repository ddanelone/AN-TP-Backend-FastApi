# services/tp6/service_inciso_d.py
import numpy as np
import time
import matplotlib.pyplot as plt
from services.tp6.numerical import D0, simular_2D_lineal, save_plot_to_buffer
from services.tp6.core import processor

_cache_d = None

def get_consigna():
    return "d) Resuelva en 2D una gota circular y verifique comparando con la solución 1D en coordenadas cilíndricas. Trate la singularidad en r=0 con cuidado."

def simular_1D_cilindrico(Lr, R_gota, h, T_final, D_val):
    start = time.time()
    Nr = int(Lr / h) + 1; r_vec = np.linspace(0, Lr, Nr)
    theta = np.zeros(Nr); theta[r_vec <= R_gota] = 1.0
    theta_new = np.zeros(Nr)
    dt = (0.20 * h**2) / D_val; Nt = int(T_final / dt); alpha = D_val * dt / h**2
    
    for _ in range(Nt):
        theta[-1] = 0.0
        theta_new[0] = theta[0] + 4.0 * alpha * (theta[1] - theta[0])
        th_i = theta[1:-1]; th_p = theta[2:]; th_m = theta[:-2]; r_i = r_vec[1:-1]
        theta_new[1:-1] = th_i + alpha * ((th_p - 2*th_i + th_m) + (h / (2.0 * r_i)) * (th_p - th_m))
        theta = theta_new.copy()
    return r_vec, theta, time.time() - start

def ic_gota(X, Y, L, R_gota):
    return np.where(np.sqrt((X - L/2)**2 + (Y - L/2)**2) <= R_gota, 1.0, 0.0)

def _run_d():
    L = 2.0; Lr = L/2; Rg = 0.4; T = 0.4; h = 0.02
    
    # 1D
    r_1d, th_1d, t1 = simular_1D_cilindrico(Lr, Rg, h, T, D0)
    
    # 2D
    start2 = time.time()
    Nx = int(L/h) + 1
    # Unpack 9 valores
    _, _, _, _, th2, _, _, _, _ = simular_2D_lineal(L, Nx, T, D0, lambda X,Y,L: ic_gota(X,Y,L,Rg))
    t2 = time.time() - start2
    
    # Registro tiempo
    processor.record_time("D", t1 + t2)
    
    return {"r": r_1d, "th1": th_1d, "th2_cut": th2[Nx//2, Nx//2:], "th2_full": th2, "t1": t1, "t2": t2, "N": Nx}

def _get_data():
    global _cache_d
    if _cache_d is None: _cache_d = _run_d()
    return _cache_d

def get_console():
    d = _get_data()
    return (
        "Ejecutando Inciso D...\n"
        f"   Simulación 1D Cilíndrica completada en {d['t1']:.2f}s\n"
        f"   Simulación 2D Cartesiana completada en {d['t2']:.2f}s\n"
        f"   (Tiempo total registrado: {d['t1']+d['t2']:.2f}s)"
    )

def get_grafico_1d():
    d = _get_data()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("Inciso (d): Comparación de Perfiles Radiales")
    ax.plot(d['r'], d['th1'], 'r-', lw=3, label="Referencia 1D")
    ax.plot(d['r'], d['th2_cut'], 'b.', ms=8, label="Corte 2D")
    ax.legend(); ax.grid(True)
    return save_plot_to_buffer(fig)

def get_grafico_2d():
    d = _get_data()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_title("Inciso (d): Gota Circular 2D")
    im = ax.imshow(d['th2_full'], origin='lower', cmap='viridis')
    fig.colorbar(im, ax=ax)
    return save_plot_to_buffer(fig)

def get_explicacion():
    return """
    **Fundamentación y Conclusiones - Inciso D (Gota Circular):**
    
    1. **Validación Cruzada:** Comparamos una simulación 2D completa (malla cartesiana) contra una 1D en coordenadas cilíndricas (referencia teórica por simetría radial).
    
    2. **El Problema de la Singularidad en $r=0$:**
       En coordenadas cilíndricas, el término $1/r$ explota en el centro.
       - **Solución:** Aplicamos la regla de L'Hôpital. En el centro, la difusión ocurre "el doble de rápido" geométricamente. La ecuación cambia a $\partial \theta / \partial t = 2 D (\partial^2 \theta / \partial r^2)$.
    
    3. **Conclusión:**
       - El perfil radial de la solución 2D coincide con la referencia 1D.
       - **Isotropía:** El mapa de calor muestra un círculo perfecto. Esto significa que nuestra malla cuadrada no distorsiona la física; la difusión viaja igual en diagonales que en los ejes (no hay anisotropía numérica significativa).
    """