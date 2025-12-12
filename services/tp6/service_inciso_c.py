# services/tp6/service_inciso_c.py
import numpy as np
import time
import matplotlib.pyplot as plt
from services.tp6.numerical import D0, simular_2D_lineal, save_plot_to_buffer
from services.tp6.core import processor

_cache_c = None

def get_consigna():
    return "c) Verifique una implementación de diferencias finitas en 2D con D constante contra una solución analítica (p. ej. solución en un rectángulo con condiciones de Dirichlet/Neumann conocidas). Mostrar convergencia en norma L2 al refinar mallas 2D."

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
    d = _get_data()
    
    # Formateo de tabla con ancho fijo para que se vea perfecta en consola
    # Usamos f-strings con alineación (^ centrado, < izquierda, > derecha)
    
    sep_line = "+" + "-"*9 + "+" + "-"*14 + "+" + "-"*16 + "+"
    header   = f"| {'N':^7} | {'dx (h)':^12} | {'Error L2':^14} |"
    
    out = [
        "Ejecutando Inciso C...",
        "   --- Ejecutando Prueba de Convergencia ---",
        sep_line,
        header,
        sep_line
    ]
    
    for r in d['logs']:
        # Fila de datos principales
        row = f"| {r['N']:^7} | {r['dx']:^12.4f} | {r['err']:^14.3e} |"
        out.append(row)
        out.append(sep_line)
        
        # Detalles técnicos adicionales debajo de cada fila (opcional, para más info)
        out.append(f"  > Config: dt={r['dt']:.5f}, Nt={r['Nt']}, alpha={r['a']:.2f}")
        out.append("") # Línea en blanco para separar iteraciones
        
    out.append(f"Convergencia completada en {d['elapsed']:.2f} segundos.")
    return "\n".join(out)

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
    return """
    **Fundamentación y Conclusiones - Inciso C:**
    
    1. **Verificación 2D:** Extendemos el esquema FTCS a dos dimensiones. La condición de estabilidad es más estricta aquí: $\alpha \le 0.25$. Usamos $\alpha=0.20$.
    
    2. **Prueba de Convergencia:**
       El objetivo no es solo ver "si da parecido", sino cuantificar **cuánto mejora** al refinar la malla.
       - Usamos la **Norma $L^2$** para medir el error global en todo el cuadrado.
    
    3. **Conclusión del Gráfico Log-Log:**
       - La pendiente de la recta de error es aproximadamente **2**.
       - Esto confirma que nuestro esquema tiene **Convergencia Cuadrática** ($O(h^2)$). Es decir, si reducimos el tamaño de la celda a la mitad, el error baja cuatro veces.
       - Esto valida matemáticamente que la matriz de diferencias finitas está bien construida.
    """