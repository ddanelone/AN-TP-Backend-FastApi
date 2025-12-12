import numpy as np
from scipy.integrate import solve_ivp

# --- CONSTANTES DEL MODELO (Del Notebook) ---
MASA = 1.6e-8        # kg
RIGIDEZ = 0.5        # N/m
COEF_AMORT = 8.3e-5  # N·s/m
Y_EQ = 1.3e-4        # m

# --- ECUACIÓN DIFERENCIAL ---
def sistema_gota(t, Y_vec):
    """Retorna [y', y''] para el sistema masa-resorte-amortiguador."""
    y, v = Y_vec
    dydt = v
    dvdt = -(COEF_AMORT / MASA) * v - (RIGIDEZ / MASA) * (y - Y_EQ)
    return [dydt, dvdt]

# --- SOLVER TAYLOR 3 ---
def get_derivs_taylor(y, v):
    dy = v
    d2y = -(COEF_AMORT / MASA) * v - (RIGIDEZ / MASA) * (y - Y_EQ)
    d3y = -(COEF_AMORT / MASA) * d2y - (RIGIDEZ / MASA) * v
    return dy, d2y, d3y

def taylor3_solver(t0, tf, y0_vec, h):
    """Método de Taylor de orden 3. Devuelve (t, y, v)."""
    if tf <= t0: tf = t0 + 0.006
    Pasos = int((tf - t0) / h)
    t_vals = np.linspace(t0, tf, Pasos + 1)
    y_vals = np.zeros(Pasos + 1)
    v_vals = np.zeros(Pasos + 1)
    y_vals[0], v_vals[0] = y0_vec
    
    for i in range(Pasos):
        dy, d2y, d3y = get_derivs_taylor(y_vals[i], v_vals[i])
        y_vals[i+1] = y_vals[i] + h*dy + (h**2/2)*d2y + (h**3/6)*d3y
        v_vals[i+1] = v_vals[i] + h*d2y + (h**2/2)*d3y
        
    return t_vals, y_vals, v_vals

# --- SOLVER ADAMS-BASHFORTH-MOULTON 4 ---
def abm4_solver(t0, tf, y0_vec, h):
    """Método Predictor-Corrector ABM4. Devuelve (t, y, v)."""
    if tf <= t0: tf = t0 + 0.006
    
    # Arranque con RK45 (scipy)
    t_span_init = [t0, t0 + 3*h]
    t_eval_init = [t0, t0+h, t0+2*h, t0+3*h]
    
    init = solve_ivp(sistema_gota, t_span_init, y0_vec, method='RK45', 
                     t_eval=t_eval_init, rtol=1e-12, atol=1e-12)
    
    Pasos = int((tf - t0) / h)
    t_vals = np.linspace(t0, tf, Pasos + 1) # <--- AQUÍ SE DEFINE t_vals
    y_store = np.zeros((Pasos + 1, 2)) # [y, v]
    
    # Rellenar arranque
    y_init_T = init.y.T 
    n_init = len(y_init_T)
    limit = min(n_init, 4)
    y_store[:limit] = y_init_T[:limit]
    
    # Historial de derivadas (f(t, y))
    f_hist = [np.array(sistema_gota(t_vals[i], y_store[i])) for i in range(limit)]
    
    # Bucle ABM (Empieza desde el paso 3 para predecir el 4)
    for i in range(3, Pasos):
        f_i  = f_hist[-1]
        f_m1 = f_hist[-2]
        f_m2 = f_hist[-3]
        f_m3 = f_hist[-4]
        
        # Predictor (AB4)
        pred = y_store[i] + (h/24)*(55*f_i - 59*f_m1 + 37*f_m2 - 9*f_m3)
        
        # Evaluamos f en la predicción
        f_pred = np.array(sistema_gota(t_vals[i+1], pred))
        
        # Corrector (AM4)
        corr = y_store[i] + (h/24)*(9*f_pred + 19*f_i - 5*f_m1 + f_m2)
        y_store[i+1] = corr
        
        # Guardamos la derivada CORREGIDA
        f_hist.append(np.array(sistema_gota(t_vals[i+1], corr)))
        
    return t_vals, y_store[:, 0], y_store[:, 1] # Retorna t, y, v

# --- INTEGRACIÓN NUMÉRICA (Trapecios y Simpson) ---
def trapecio_integrator(y_vals, dx):
    return dx * (0.5 * y_vals[0] + np.sum(y_vals[1:-1]) + 0.5 * y_vals[-1])

def simpson_integrator(y_vals, dx):
    N = len(y_vals)
    if N < 3: return trapecio_integrator(y_vals, dx)
    
    if N % 2 == 0: 
        return simpson_integrator(y_vals[:-1], dx) + 0.5 * dx * (y_vals[-2] + y_vals[-1])
    
    return (dx / 3) * (y_vals[0] + 4 * np.sum(y_vals[1:-1:2]) + 2 * np.sum(y_vals[2:-2:2]) + y_vals[-1])

def integrar_perfil_detalle(x_perfil, y_perfil):
    if len(y_perfil) < 2: return 0, 0, 0, 0
    
    dy = y_perfil[1] - y_perfil[0]
    
    # Volumen
    integrando_vol = np.pi * x_perfil**2
    v_trap = trapecio_integrator(integrando_vol, dy)
    v_simp = simpson_integrator(integrando_vol, dy)
    
    # Área
    dx_dy = np.gradient(x_perfil, dy)
    ds = np.sqrt(1 + dx_dy**2)
    integrando_area = 2 * np.pi * x_perfil * ds
    
    a_trap = trapecio_integrator(integrando_area, dy)
    a_simp = simpson_integrator(integrando_area, dy)
    
    return v_trap, v_simp, a_trap, a_simp