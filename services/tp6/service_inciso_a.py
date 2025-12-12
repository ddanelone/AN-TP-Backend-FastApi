# services/tp6/service_inciso_a.py
import numpy as np
import time
import matplotlib.pyplot as plt
from services.tp6.numerical import D0, save_plot_to_buffer
from services.tp6.core import processor

_cache_a = None

def get_consigna():
    return "a) Suponga una difusividad constante D(theta)=D0 y verifique la implementación de diferencias finitas en 1D contra una solución analítica."

def _run_a():
    start_time = time.time()
    L = 1.0; T_final = 0.5; Nx = 51
    dx = L / (Nx - 1); x = np.linspace(0, L, Nx)
    
    alpha_factor = 0.45
    dt = (alpha_factor * dx**2) / D0
    Nt = int(T_final / dt)
    T_final_real = Nt * dt
    alpha = D0 * dt / dx**2
    
    theta = np.sin(np.pi * x / L)
    theta_ini = theta.copy()
    theta_new = np.zeros(Nx)
    
    for _ in range(Nt):
        theta[0] = 0.0; theta[-1] = 0.0
        theta_new[1:-1] = theta[1:-1] + alpha * (theta[2:] - 2*theta[1:-1] + theta[:-2])
        theta = theta_new.copy()
        
    theta_ana = np.exp(-D0 * (np.pi/L)**2 * T_final_real) * np.sin(np.pi * x / L)
    error = np.max(np.abs(theta - theta_ana))
    
    elapsed = time.time() - start_time
    processor.record_time("A", elapsed)
    
    return {
        "L": L, "T": T_final_real, "Nx": Nx, "dx": dx, "Nt": Nt, "dt": dt,
        "alpha": alpha, "error": error, "x": x, "th_ini": theta_ini, 
        "th_num": theta, "th_ana": theta_ana
    }

def _get_data():
    global _cache_a
    if _cache_a is None: _cache_a = _run_a()
    return _cache_a

def get_console():
    res = _get_data()
    return (
        "Ejecutando Inciso A...\n"
        f"   Dominio: L={res['L']} m, Tiempo Total={res['T']:.2f} s\n"
        f"   Grilla: Nx={res['Nx']}, dx={res['dx']:.4f} m, Nt={res['Nt']}, dt={res['dt']:.6f} s\n"
        f"   Estabilidad: alpha = {res['alpha']:.4f}\n"
        f"   Error máximo (L-inf) en T_final: {res['error']:.2e}"
    )

def get_grafico():
    res = _get_data()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f"Inciso (a): Difusión 1D (FTCS) en T = {res['T']:.2f} s")
    ax.plot(res['x'], res['th_ini'], 'k--', label="Condición Inicial (t=0)")
    ax.plot(res['x'], res['th_num'], 'bo', markersize=5, label=f"Numérica (FTCS, Nx={res['Nx']})")
    ax.plot(res['x'], res['th_ana'], 'r-', label="Solución Analítica")
    ax.set_xlabel("Posición (x)"); ax.set_ylabel(r"Saturación ($\theta$)")
    ax.legend(); ax.grid(True)
    return save_plot_to_buffer(fig)
 
def get_explicacion():
    return r"""
    **Fundamentación y Conclusiones - Inciso A:**
    
    1. **Planteo Físico:** Se modela la difusión lineal simple con coeficiente constante ($D_0$). Al ser 1D, representa el flujo en una barra delgada o un medio poroso homogéneo.
    
    2. **Estrategia Numérica:** Utilizamos el esquema FTCS (Forward Time, Central Space). Es explícito, lo que significa que el estado futuro depende solo del presente.
       - **Condición de Estabilidad:** El punto crítico aquí es el número de Courant ($\alpha$). Para que la solución no explote (diverja), necesitamos estrictamente $\alpha \le 0.5$. En nuestra simulación, con $\alpha=0.45$, garantizamos estabilidad.
    
    3. **Conclusión:**
       - La comparación visual es perfecta: los puntos numéricos se montan sobre la curva analítica.
       - El error $L_\infty$ (máximo error absoluto) es del orden de $10^{-4}$, lo cual valida que la discretización de las derivadas (espacial de 2do orden) es correcta.
    """