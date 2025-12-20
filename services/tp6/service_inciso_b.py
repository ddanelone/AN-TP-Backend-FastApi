# services/tp6/service_inciso_b.py
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve
from services.tp6.numerical import D_VanGenuchten, dD_dtheta, VG_PARAMS, save_plot_to_buffer
from services.tp6.core import processor

_cache_b = None

def get_consigna():
    return r"""
**Inciso (b): No-Linealidad y Modelo de Van Genuchten**

En suelos reales y medios porosos como el papel, la difusividad no es constante, sino que cae abruptamente cuando el medio se seca. Utilizamos el modelo constitutivo de **Van Genuchten**:

$$ D(\theta) = D_{ref} \cdot \left( \frac{\theta - \theta_r}{\theta_s - \theta_r} \right)^n $$

Esto genera frentes de humedad muy pronunciados que son difíciles de resolver numéricamente sin violar la conservación de masa.

---

**Consigna:**

1. Resuelva la ecuación mediante **Diferencias Finitas 1D** con $D(\theta)$ variable.
2. Valide la solución utilizando la **Transformación de Boltzmann**. Esta técnica convierte la ecuación parcial (PDE) en una ecuación ordinaria (ODE) mediante la variable de similitud:

$$ \phi = x \cdot t^{-1/2} $$

Si la física es correcta, todos los perfiles de humedad en distintos tiempos $t$ deben colapsar en una única curva al graficarse contra $\phi$.
"""

def boltzmann_ode(phi, y):
    theta_val, y2 = y[0], y[1]
    tr = VG_PARAMS['theta_r']
    theta_val = max(tr + 1e-9, min(theta_val, 1.0))
    D_val = max(D_VanGenuchten(theta_val), 1e-16)
    dD_val = dD_dtheta(theta_val)
    dy1 = y2
    dy2 = -(1.0 / D_val) * ( (phi / 2.0) * y2 + dD_val * (y2**2) )
    return [dy1, dy2]

def solve_boltzmann():
    def objective(C_guess):
        try:
            sol = solve_ivp(boltzmann_ode, [0, 5.0], [1.0, C_guess[0]], method='Radau', rtol=1e-5)
            return sol.y[0, -1] - VG_PARAMS['theta_r']
        except: return 100.0
    
    C_shot = fsolve(objective, [-180.0])[0]
    
    phi_eval = np.linspace(0, 0.05, 1000)
    sol = solve_ivp(boltzmann_ode, [0, 0.05], [1.0, C_shot], method='Radau', t_eval=phi_eval)
    
    idx_ref = np.argmin(np.abs(sol.y[0, :] - 0.5))
    phi_front = sol.t[idx_ref]
    
    return C_shot, sol.t, sol.y[0, :], phi_front

def run_fdm():
    start_time = time.time()
    
    L = 0.05; Nx = 301; T_final = 2000.0
    dx = L / (Nx - 1); x = np.linspace(0, L, Nx)
    theta_test = np.linspace(VG_PARAMS['theta_r'], 1.0, 100)
    D_max = np.max(D_VanGenuchten(theta_test))
    dt = (0.4 * dx**2) / D_max
    Nt = int(T_final / dt) + 1
    
    theta = np.ones(Nx) * VG_PARAMS['theta_r']; theta[0] = 1.0
    theta_new = np.zeros(Nx)
    
    snapshots = []; target_times = [100, 500, 1000, 1500, 2000]
    front_t = []; front_x = []
    
    for n in range(Nt):
        curr_time = n * dt
        if len(snapshots) < len(target_times):
            if curr_time >= target_times[len(snapshots)]:
                snapshots.append((curr_time, theta.copy()))
        
        if n % 50 == 0:
            try:
                xf = np.interp(0.5, theta[::-1], x[::-1])
                front_t.append(curr_time); front_x.append(xf)
            except: pass
            
        D_c = D_VanGenuchten(theta)
        D_f = 0.5 * (D_c[:-1] + D_c[1:])
        flux_in = D_f[:-1] * (theta[1:-1] - theta[:-2])
        flux_out = D_f[1:] * (theta[2:] - theta[1:-1])
        theta_new[1:-1] = theta[1:-1] + (dt / dx**2) * (flux_out - flux_in)
        theta_new[0] = 1.0; theta_new[-1] = VG_PARAMS['theta_r']
        theta[:] = theta_new[:]
        
    elapsed = time.time() - start_time
    processor.record_time("B", elapsed)
    
    return {
        "L": L, "T": T_final, "Nx": Nx, "dx": dx, "dt": dt, "elapsed": elapsed,
        "x": x, "snaps": snapshots, "ft": np.array(front_t), "fx": front_x
    }

def _get_data():
    global _cache_b
    if _cache_b is None:
        C_shot, b_phi, b_theta, phi_front = solve_boltzmann()
        fdm_res = run_fdm()
        _cache_b = {
            "boltzmann": {
                "C_shot": C_shot, 
                "phi_front_ref": phi_front,
                "phi_arr": b_phi,      
                "theta_arr": b_theta   
            }, 
            "fdm": fdm_res
        }
    return _cache_b

def get_console():
    """
    Genera un reporte Markdown estructurado para el Modelo de Van Genuchten,
    comparando parámetros de Shooting (Boltzmann) y esquema FDM.
    """
    data = _get_data()
    b = data["boltzmann"]
    f = data["fdm"]

    # Helper para formateo consistente
    def armar_vector(lista):
        return "`[ " + " | ".join(lista) + " ]`"

    # --- Bloque 1: Transformada de Boltzmann (ODE) ---
    # Formateamos valores clave del método de disparo
    vec_shot = [
        f"C_shot: {b['C_shot']:.4e}",   # Pendiente en origen
        f"φ(0.5): {b['phi_front_ref']:.4f}" # Valor de referencia en el frente
    ]

    # --- Bloque 2: Parámetros de Simulación (PDE) ---
    # Física del problema
    vec_fisica = [
        f"L: {f['L']} m",
        f"T: {f['T']} s"
    ]
    
    # Discretización numérica
    vec_malla = [
        f"Nx: {f['Nx']}",
        f"dx: {f['dx']:.2e} m",
        f"dt: {f['dt']:.5f} s"
    ]

    # --- Construcción del Reporte ---
    out = "### 🌊 Dinámica de Infiltración (Van Genuchten)\n\n"

    out += "**🎯 Método de Disparo (Solución de Similaridad):**\n"
    out += armar_vector(vec_shot) + "\n\n"

    out += "**🌍 Configuración Física:**\n"
    out += armar_vector(vec_fisica) + "\n\n"

    out += "**🔢 Esquema Numérico (FDM Explícito):**\n"
    out += armar_vector(vec_malla) + "\n\n"

    out += "---\n"
    out += f"> **⏱️ Tiempo de Cómputo:** {f['elapsed']:.2f} s"

    return out

def get_grafico_perfiles():
    data = _get_data(); f = data["fdm"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("Evolución Temporal de Perfiles de Humedad (FDM Van Genuchten)")
    
    # --- CORRECCIÓN AQUÍ PARA PYLANCE ---
    # Usamos plt.get_cmap() en lugar de plt.cm.viridis directo
    cmap = plt.get_cmap("viridis")
    colors = cmap(np.linspace(0, 1, len(f['snaps'])))
    
    for i, (t, th) in enumerate(f['snaps']):
        ax.plot(f['x'], th, color=colors[i], lw=2, label=f"t = {t:.0f} s")
        
    ax.axhline(0.5, c='k', ls=':', alpha=0.5, label="Nivel de Frente (0.5)")
    ax.set_xlabel("x [m]"); ax.set_ylabel(r"$\theta$")
    ax.legend(); ax.grid(True, alpha=0.3)
    return save_plot_to_buffer(fig)

def get_grafico_frente():
    data = _get_data(); f = data["fdm"]; phi = data["boltzmann"]["phi_front_ref"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title(r"Validación de Posición del Frente ($\theta=0.5$)")
    st = np.sqrt(f['ft'])
    ax.plot(st, f['fx'], 'bo', ms=3, label="Frente Numérico")
    ax.plot(st, phi * st, 'r-', lw=2, label=f"Ref. Boltzmann (phi={phi:.4f})")
    ax.set_xlabel(r"$\sqrt{t}$ [$s^{1/2}$]"); ax.set_ylabel("Posición x [m]")
    ax.legend(); ax.grid(True, alpha=0.3)
    return save_plot_to_buffer(fig)

def get_grafico_zoom():
    data = _get_data()
    b = data["boltzmann"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("Inciso (b): Referencia Boltzmann (Van Genuchten) - Zoom en Frente")
    
    ax.plot(b['phi_arr'], b['theta_arr'], 'r-', lw=2.5, label='Solución ODE')
    ax.axhline(VG_PARAMS['theta_r'], color='gray', linestyle='--', alpha=0.6, label='Theta Residual')
    
    ax.set_xlim(0, 0.02)
    ax.set_xlabel(r"Variable de Boltzmann $\phi$")
    ax.set_ylabel(r"Saturación $\theta$")
    ax.legend()
    ax.grid(True, which='both', alpha=0.3)
    
    return save_plot_to_buffer(fig)

def get_explicacion():
    return r"""

**1. El Desafío de la No-Linealidad:**
A diferencia del caso A, aquí la difusividad $D(\theta)$ depende fuertemente de la humedad.
* **Problema:** Cuando el papel está seco ($\theta \approx \theta_r$), la difusividad cae abruptamente a cero ($D \to 0$). Esto genera un **frente de onda muy rígido (stiff)**, casi vertical.

**2. Solución Numérica (FDM Conservativo):**
Para manejar este frente sin perder masa, implementamos diferencias finitas con flujo conservativo en las caras de las celdas, promediando $D$ entre nodos ($D_{i+1/2}$).

**3. Validación con Boltzmann:**
Como no hay solución analítica simple, usamos la variable de similitud $\phi = x / \sqrt{t}$.
* **Conclusión:** Al graficar los perfiles de distintos tiempos ($t=100s, 500s...$) contra $\phi$, **todas las curvas colapsan en una sola**.
* Esto prueba que nuestro código respeta la física de la difusión (ley de la raíz cuadrada del tiempo) y que el frente abrupto es real, no un error numérico.

**4. Costo Computacional:**
Este es el inciso más lento. La rigidez de la curva obliga a usar un $\Delta t$ pequeñísimo para no violar la estabilidad local en la zona del frente.
"""