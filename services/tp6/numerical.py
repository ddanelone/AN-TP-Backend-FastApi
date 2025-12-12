# services/tp6/numerical.py
import numpy as np
import matplotlib.pyplot as plt
import io

# --- Constantes Físicas Generales ---
D0 = 0.1

# --- Parámetros Van Genuchten (Papel Whatman 1 - Tabla 1) ---
VG_PARAMS = {
    'theta_r': 0.004943,
    'theta_s': 1.0,
    'n': 2.344,
    'Ks_over_alpha': 2.079e-6
}
# Calculamos m una sola vez
VG_PARAMS['m'] = 1.0 - (1.0 / VG_PARAMS['n'])

# --- Modelos Constitutivos ---
def D_VanGenuchten(theta):
    """Modelo de Difusividad de Van Genuchten-Mualem."""
    tr = VG_PARAMS['theta_r']
    ts = VG_PARAMS['theta_s']
    m = VG_PARAMS['m']
    Ks_alpha = VG_PARAMS['Ks_over_alpha']
    
    # Clip para evitar valores no físicos y división por cero
    theta_safe = np.clip(theta, tr + 1e-9, ts)
    Se = (theta_safe - tr) / (ts - tr)
    
    # Constante de referencia D_ref
    D_ref = ((1.0 - m) * Ks_alpha) / (m * (ts - tr))
    
    term1 = np.sqrt(Se)
    term2 = (1.0 - (1.0 - Se**(1.0/m))**m)**2
    
    return D_ref * term1 * term2

def dD_dtheta(theta):
    """Derivada numérica de D(theta) para el método de Boltzmann."""
    epsilon = 1e-5
    d_plus = D_VanGenuchten(theta + epsilon)
    d_minus = D_VanGenuchten(theta - epsilon)
    return (d_plus - d_minus) / (2 * epsilon)

# --- Solvers Genéricos ---

def simular_2D_lineal(L, N, T_final, D_coef, CI_func, alpha_factor=0.20):
    """
    Solver genérico para difusión 2D lineal (D constante).
    Retorna 9 valores: x, y, X, Y, theta, T_real, dt, Nt, alpha
    """
    Nx = Ny = N
    h = L / (Nx - 1)
    x = np.linspace(0, L, Nx)
    y = np.linspace(0, L, Ny)
    X, Y = np.meshgrid(x, y)

    # Estabilidad
    dt = (alpha_factor * h**2) / D_coef
    Nt = int(T_final / dt)
    T_final_real = Nt * dt
    alpha = D_coef * dt / h**2

    # Inicialización
    theta = CI_func(X, Y, L)
    theta_new = np.zeros((Ny, Nx))

    # Bucle temporal (Vectorizado para velocidad)
    for _ in range(Nt):
        # Condiciones de borde (Dirichlet 0)
        theta[0, :] = 0.0; theta[-1, :] = 0.0
        theta[:, 0] = 0.0; theta[:, -1] = 0.0
        
        # Diferencias Finitas (Stencil de 5 puntos)
        term_x = theta[1:-1, 2:] - 2*theta[1:-1, 1:-1] + theta[1:-1, :-2]
        term_y = theta[2:, 1:-1] - 2*theta[1:-1, 1:-1] + theta[:-2, 1:-1]
        
        theta_new[1:-1, 1:-1] = theta[1:-1, 1:-1] + alpha * (term_x + term_y)
        theta = theta_new.copy()

    # CORRECCIÓN: Se agregan Nt y alpha al return
    return x, y, X, Y, theta, T_final_real, dt, Nt, alpha

# --- Utilidades de Gráficos ---
def save_plot_to_buffer(fig):
    """Convierte una figura de Matplotlib a un buffer de bytes para FastAPI."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig) # Liberar memoria
    return buf