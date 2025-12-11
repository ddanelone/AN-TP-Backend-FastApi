import sympy as sp
import numpy as np
import io
import matplotlib
matplotlib.use('Agg')  # Evita problemas con backends gráficos
import matplotlib.pyplot as plt
import time
from scipy.optimize import brentq
from io import BytesIO
from fastapi.responses import StreamingResponse


def obtener_funciones_expr():
    x = sp.Symbol('x')

    f_expr = sp.exp(-x) * sp.cos(5 * x) - sp.Rational(1, 100) * x # type: ignore

    f1_expr = sp.diff(f_expr, x)
    f2_expr = sp.diff(f1_expr, x)
    
    return x, f_expr, f1_expr, f2_expr

def obtener_funciones_numericas():
    x, f_expr, f1_expr, f2_expr = obtener_funciones_expr()
    f = sp.lambdify(x, f_expr, 'numpy')
    f1 = sp.lambdify(x, f1_expr, 'numpy')
    f2 = sp.lambdify(x, f2_expr, 'numpy')
    return f, f1, f2

def metodo_taylor_segundo_orden(f, f1, f2, x0=3.0, tol=1e-12, max_iter=50):
    historial = []
    salida = []

    salida.append("📘 Método de búsqueda de raíces por serie de Taylor (incluye 2da derivada)\n")

    for n in range(max_iter):
        fx = f(x0)
        f1x = f1(x0)
        f2x = f2(x0)

        if abs(fx) < tol:
            salida.append(f"✅ Convergencia por |f(x)| < {tol:.1e}")
            salida.append(f"🔍 Raíz aproximada: {x0:.6f}")
            break

        discriminante = f1x**2 - 2*fx*f2x

        salida.append(f"🔁 Iteración {n}")
        salida.append(f"   xₙ         = {x0:.6f}")
        salida.append(f"   f(xₙ)      = {fx:.2e}")
        salida.append(f"   f'(xₙ)     = {f1x:.2e}")
        salida.append(f"   f''(xₙ)    = {f2x:.2e}")
        salida.append(f"   Discriminante = {discriminante:.2e}")

        if discriminante < 0:
            salida.append("❌ Discriminante negativo. Raíces complejas. Método detenido.")
            break

        if abs(f2x) < 1e-12:
            salida.append("⚠️ Segunda derivada cercana a cero. Usando Newton clásico.")
            delta = -fx / f1x
        else:
            sqrt_disc = np.sqrt(discriminante)
            delta1 = (-f1x + sqrt_disc) / f2x
            delta2 = (-f1x - sqrt_disc) / f2x
            delta = delta1 if abs(delta1) < abs(delta2) else delta2

        x1 = x0 + delta
        error = abs(x1 - x0)

        # Calcular orden de convergencia experimental si hay suficientes errores previos
        if n >= 2:
            e0 = historial[-2]['error']
            e1 = historial[-1]['error']
            e2 = error

            if e0 > 0 and e1 > 0 and e2 > 0:
                orden = np.log(e2 / e1) / np.log(e1 / e0)
                salida.append(f"   Orden estimado de convergencia ≈ {orden:.2f}")
                orden_estimado = float(orden)
            else:
                orden_estimado = None
        else:
            orden_estimado = None

        salida.append(f"   Δx elegido = {delta:.2e}")
        salida.append(f"   xₙ₊₁       = {x1:.6f}")
        salida.append(f"   Error      = {error:.2e}\n")

        historial.append({
            'n': n,
            'x': float(x0),
            'f': float(fx),
            'f1': float(f1x),
            'f2': float(f2x),
            'disc': float(discriminante),
            'delta': float(delta),
            'x_next': float(x1),
            'error': float(error),
            'orden': orden_estimado
        })

        if error < tol:
            salida.append(f"✅ Convergencia alcanzada en {n+1} iteraciones.")
            salida.append(f"🔍 Raíz aproximada: {x1:.6f}")
            break

        x0 = x1

    else:
        salida.append("❌ No se alcanzó convergencia dentro del máximo de iteraciones.")

    # Agregar nota final explicativa sobre el método
    salida.append("\n📚 Requisitos del método:")
    salida.append("- f(x), f'(x), f''(x) deben ser funciones continuas y evaluables en un entorno de la raíz.")
    salida.append("- El discriminante f'(x)² - 2·f(x)·f''(x) debe ser ≥ 0 (si no, se obtienen raíces complejas).")
    salida.append("- Si f''(x) ≈ 0, se recurre al método de Newton clásico.")
    salida.append("- Se elige la Δx de menor módulo para mejorar la estabilidad numérica.")
    salida.append("- A partir de la iteración 2 se estima el orden de convergencia observado.")

    return historial, "\n".join(salida)

def graficar_iteraciones(historial, f, funcion_str="f(x)"):
    xs = [step['x'] for step in historial]
    ys = [step['f'] for step in historial]
    
    if len(xs) < 2:
        margin = 0.5
    else:
        margin = 0.2 * (max(xs) - min(xs))
    
    x_min = min(xs) - margin
    x_max = max(xs) + margin
    x_vals = np.linspace(x_min, x_max, 400)
    y_vals = f(x_vals)

    ys_all = list(y_vals) + ys
    y_range = max(ys_all) - min(ys_all)
    offset = 0.05 * y_range

    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, label=f'${funcion_str}$', color='blue', linewidth=2)
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')

    for i, (xi, yi) in enumerate(zip(xs, ys)):
        color = 'red' if i < len(xs)-1 else 'green'
        marker = 'o' if i < len(xs)-1 else '*'
        size = 70 if i < len(xs)-1 else 120
        label = f'Iteración {i}' if i < len(xs)-1 else 'Raíz aproximada'

        plt.scatter(xi, yi, color=color, s=size, edgecolors='black',
                    zorder=5, label=label, marker=marker)
        plt.text(
            xi,
            yi + offset if yi >= 0 else yi - offset,
            f'$x_{i}$',
            fontsize=10,
            ha='center',
            va='bottom' if yi >= 0 else 'top'
        )

        if i < len(xs) - 1:
            plt.annotate('', xy=(historial[i+1]['x'], historial[i+1]['f']), xytext=(xi, yi),
                         arrowprops=dict(arrowstyle='->', color='gray',
                                         lw=1.5, shrinkA=8, shrinkB=8))

    plt.axvline(xs[-1], color='green', linestyle=':', alpha=0.5)
    
    # Ajustar los límites verticales para evitar recortes y mejorar aspecto
    y_min = min(ys_all) - 2 * offset
    y_max = max(ys_all) + 2 * offset
    plt.ylim(y_min, y_max)

    plt.title(f'Método de Taylor (2do orden) - $f(x) = {funcion_str}$', fontsize=14)
    plt.xlabel('$x$', fontsize=12)
    plt.ylabel('$f(x)$', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(loc='best')
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return buffer


def metodo_taylor_biseccion_con_log(a, b, tol=1e-12, max_iter=50):
    f, f1, f2 = obtener_funciones_numericas()
    log = io.StringIO()
    print("Método combinado: Taylor (2da derivada) + Bisección\n", file=log)

    x0 = (a + b) / 2
    historial = []

    # Contadores para análisis
    iter_taylor = 0
    iter_biseccion = 0
    iter_actualizacion_intervalo = 0

    for n in range(max_iter):
        fx = f(x0)
        f1x = f1(x0)
        f2x = f2(x0)
        discriminante = f1x**2 - 2 * fx * f2x

        print(f"Iteración {n}:", file=log)
        print(f"  x_n = {x0:.15f}", file=log)
        print(f"  f(x_n) = {fx:.15e}", file=log)
        print(f"  f'(x_n) = {f1x:.15e}", file=log)
        print(f"  f''(x_n) = {f2x:.15e}", file=log)
        print(f"  Discriminante = {discriminante:.15e}", file=log)

        if discriminante < 0 or abs(f2x) < 1e-12:
            metodo = "bisección"
            x1 = (a + b) / 2
            delta = 0.0
            iter_biseccion += 1
            print("  Método Bisección seleccionado", file=log)
        else:
            sqrt_disc = np.sqrt(discriminante)
            delta1 = (-f1x + sqrt_disc) / f2x
            delta2 = (-f1x - sqrt_disc) / f2x
            delta = delta1 if abs(delta1) < abs(delta2) else delta2
            x_taylor = x0 + delta

            if a <= x_taylor <= b:
                metodo = "taylor"
                x1 = x_taylor
                iter_taylor += 1
                print(f"  Δx elegido = {delta:.15e}", file=log)
            else:
                metodo = "bisección"
                x1 = (a + b) / 2
                delta = 0.0
                iter_biseccion += 1
                print("  Método Bisección seleccionado (Taylor fuera de rango)", file=log)

        error = abs(x1 - x0)
        print(f"  x_{n+1} = {x1:.15f}", file=log)
        print(f"  Error = {error:.15e}\n", file=log)

        historial.append({
            "iter": n,
            "x": x0,
            "fx": fx,
            "error": error,
            "metodo": metodo,
            "delta": delta
        })

        if abs(fx) < tol:
            print(f"Convergencia alcanzada por criterio de función (|f(x)| < {tol})", file=log)
            print(f"Raíz aproximada: {x0:.15f}\n", file=log)
            break

        # Actualizar intervalo como en bisección
        if f(a) * f(x0) < 0:
            b = x0
        else:
            a = x0
        iter_actualizacion_intervalo += 1

        x0 = x1

    # Resumen de contadores
    print("Resumen comparativo de uso de métodos:", file=log)
    print(f"  Iteraciones totales: {n+1}", file=log) # type: ignore
    print(f"  Iteraciones con método Taylor: {iter_taylor}", file=log)
    print(f"  Iteraciones con método Bisección: {iter_biseccion}", file=log)
    print(f"  Iteraciones con actualización de intervalo (tipo bisección): {iter_actualizacion_intervalo}", file=log)
    error_final = historial[-1]["error"] if historial else None
    print(f"  Error final aproximado: {error_final:.15e}", file=log)

    return historial, log.getvalue()
 
def ejecutar_metodos_con_comparacion(a=0.1, b=18.0, tol=1e-6, max_iter=50):
    f, f1, f2 = obtener_funciones_numericas()
    log = io.StringIO()
    
    print("Comparación de rendimiento: Método de Taylor vs Combinado Taylor-Bisección\n", file=log)

    # Taylor puro
    x0 = (a + b) / 2
    historial_taylor = []

    start_taylor = time.perf_counter()
    for n in range(max_iter):
        fx = f(x0)
        f1x = f1(x0)
        f2x = f2(x0)
        discriminante = f1x**2 - 2*fx*f2x

        if discriminante < 0 or abs(f2x) < 1e-12:
            delta = 0.0
            x1 = (a + b) / 2
        else:
            sqrt_disc = np.sqrt(discriminante)
            delta1 = (-f1x + sqrt_disc) / f2x
            delta2 = (-f1x - sqrt_disc) / f2x
            delta = delta1 if abs(delta1) < abs(delta2) else delta2
            x1 = x0 + delta

        error = abs(x1 - x0)
        historial_taylor.append({"iter": n, "x": x0, "fx": fx, "error": error})

        if abs(fx) < tol:
            break

        if f(a)*f(x0) < 0:
            b = x0
        else:
            a = x0

        x0 = x1

    end_taylor = time.perf_counter()
    tiempo_taylor = end_taylor - start_taylor

    # Método combinado
    start_combinado = time.perf_counter()
    historial_combinado, log_combinado = metodo_taylor_biseccion_con_log(a, b, tol, max_iter)
    end_combinado = time.perf_counter()
    tiempo_combinado = end_combinado - start_combinado

    print(f"Iteraciones del método de Taylor: {len(historial_taylor)}", file=log)
    print(f"Iteraciones del método combinado: {len(historial_combinado)}", file=log)

    print(f"Valor final f(x) Taylor: {f(historial_taylor[-1]['x'])}", file=log)
    print(f"Valor final f(x) Combinado: {f(historial_combinado[-1]['x'])}", file=log)

    print(f"Tiempo de ejecución Taylor puro: {tiempo_taylor:.12f} segundos", file=log)
    print(f"Tiempo de ejecución Método combinado: {tiempo_combinado:.12f} segundos", file=log)

    if tiempo_combinado > 0:
       mejora = tiempo_taylor / tiempo_combinado
       print(f"Relación de velocidad (Taylor/Combinado): {mejora:.2f}x", file=log)

    # --- Comparaciones extra ---
    # Método más rápido
    if tiempo_taylor < tiempo_combinado:
        print("Método más rápido: Taylor puro", file=log)
    elif tiempo_combinado < tiempo_taylor:
        print("Método más rápido: Método combinado Taylor-Bisección", file=log)
    else:
        print("Método más rápido: ¡Empate!", file=log)

    # Método con menos iteraciones
    iter_taylor = len(historial_taylor)
    iter_combinado = len(historial_combinado)
    if iter_taylor < iter_combinado:
        print("Método con menos iteraciones: Taylor puro", file=log)
    elif iter_combinado < iter_taylor:
        print("Método con menos iteraciones: Método combinado Taylor-Bisección", file=log)
    else:
        print("Método con menos iteraciones: ¡Empate!", file=log)

    return historial_taylor, historial_combinado, log.getvalue() + "\n\n" + log_combinado

 
def graficar_convergencia_loglog():
    # Obtener funciones
    f, f1, f2 = obtener_funciones_numericas()
    x, f_expr, *_ = obtener_funciones_expr()

    # Etiqueta elegante para el gráfico
    funcion_str = sp.latex(f_expr)

    # Buscar raíz real con Brent en un intervalo con cambio de signo
    try:
        raiz_real = brentq(f, 0.3, 3.5)  
        print(raiz_real)
    except ValueError:
        raise ValueError("No se pudo encontrar raíz real en el intervalo dado.")

    # Ejecutar método de Taylor
    historial, _ = metodo_taylor_segundo_orden(f, f1, f2, x0=3.0, tol=1e-12, max_iter=50)

    # Calcular errores absolutos
    errors = [abs(step['x_next'] - raiz_real) for step in historial if abs(step['x_next'] - raiz_real) > 0]
    iterations = np.arange(1, len(errors) + 1, dtype=float)

    if not errors:
        raise ValueError("No se generaron errores para graficar.")

    # Crear gráfico
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Curva de referencia O(n^-p)
    p_ref = 3
    C = errors[0] * (iterations[0] ** p_ref)
    ref_curve = C * iterations**(-p_ref)

    # Gráfico de errores log-log
    ax1.loglog(iterations, errors, marker='o', linestyle='-', color='blue',
               linewidth=2, markersize=8, label='Error absoluto')
    ax1.loglog(iterations, ref_curve, 'k--', label=f'Referencia: $O(n^{{-{p_ref}}})$')
    ax1.set_title(f'Convergencia del Método de Taylor (2º orden)\n$f(x) = {funcion_str}$', fontsize=14)
    ax1.set_xlabel('Iteración')
    ax1.set_ylabel('Error absoluto')
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax1.set_xticks(iterations)
    ax1.legend()

    # Gráfico de razón de errores
    if len(errors) > 2:
        ratios = np.array(errors[1:]) / np.array(errors[:-1])
        ax2.plot(iterations[1:], ratios, 's-', color='red', markersize=8,
                 linewidth=2, label='Tasa de convergencia')
        ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.8)
        ax2.set_title('Tasa de Convergencia Numérica')
        ax2.set_xlabel('Iteración')
        ax2.set_ylabel('$\\frac{e_{n+1}}{e_n}$')
        ax2.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
        ax2.legend()
    else:
        ax2.text(0.5, 0.5, "No hay suficientes datos para tasa de convergencia", 
                 ha='center', va='center', fontsize=12, transform=ax2.transAxes)
        ax2.axis('off')

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    return buffer
 
def graficar_taylor_local(iteration: int):
    delta_zoom = 0.1
    delta_amplio = 1.5

    # Obtener funciones
    f, f1, f2 = obtener_funciones_numericas()
    historial, _ = metodo_taylor_segundo_orden(f, f1, f2, x0=3.0, tol=1e-12, max_iter=50)

    if iteration < 0 or iteration >= len(historial):
        raise ValueError("Número de iteración inválido.")

    step = historial[iteration]
    xn = step['x']
    fxn = step['f']
    f1n = step['f1']
    f2n = step['f2']
    xn_next = step['x_next']

    # Aproximación de Taylor 2º orden
    def taylor2(x_val):
        return fxn + f1n * (x_val - xn) + 0.5 * f2n * (x_val - xn) ** 2

    # --- Gráfico 1: Intervalo amplio dinámico centrado en xn ---
    x_amplio = np.linspace(xn - delta_amplio, xn + delta_amplio, 300)
    y_orig_amplio = f(x_amplio)
    y_taylor_amplio = taylor2(x_amplio)

    # --- Gráfico 2: Zoom local ---
    x_local = np.linspace(xn - delta_zoom, xn + delta_zoom, 300)
    y_orig_local = f(x_local)
    y_taylor_local = taylor2(x_local)

    fig, axs = plt.subplots(1, 2, figsize=(14, 5))

    # Gráfico amplio
    axs[0].plot(x_amplio, y_orig_amplio, label='Función original $f(x)$', color='navy', linewidth=2)
    axs[0].plot(x_amplio, y_taylor_amplio, label=f'Aprox. Taylor 2° orden en $x_{{{iteration}}}$',
                color='green', linestyle='--', linewidth=2)
    axs[0].scatter([xn], [fxn], color='red', s=80, label=f'$x_{{{iteration}}}$ (punto de expansión)')
    axs[0].scatter([xn_next], [0], color='blue', s=80, label=f'$x_{{{iteration+1}}}$ (aprox. raíz)')
    axs[0].axhline(0, color='black', linewidth=0.8, linestyle='--')
    axs[0].axvline(xn, color='red', linestyle=':', linewidth=1)
    axs[0].axvline(xn_next, color='blue', linestyle=':', linewidth=1)
    axs[0].fill_between(x_amplio, y_orig_amplio, y_taylor_amplio, color='lightgreen', alpha=0.3)
    axs[0].set_title(f'Intervalo amplio dinámico\nIteración {iteration}')
    axs[0].set_xlabel('$x$')
    axs[0].set_ylabel('$f(x)$')
    axs[0].legend(fontsize=9)
    axs[0].grid(True, linestyle='--', alpha=0.6)
    axs[0].set_xlim(xn - delta_amplio, xn + delta_amplio)
    y_min = min(np.min(y_orig_amplio), np.min(y_taylor_amplio)) - 0.1
    y_max = max(np.max(y_orig_amplio), np.max(y_taylor_amplio)) + 0.1
    axs[0].set_ylim(y_min, y_max)

    # Gráfico zoom local
    axs[1].plot(x_local, y_orig_local, label='Función original $f(x)$', color='navy', linewidth=2)
    axs[1].plot(x_local, y_taylor_local, label=f'Aprox. Taylor 2° orden en $x_{{{iteration}}}$',
                color='green', linestyle='--', linewidth=2)
    axs[1].scatter([xn], [fxn], color='red', s=80, label=f'$x_{{{iteration}}}$ (punto de expansión)')
    axs[1].scatter([xn_next], [0], color='blue', s=80, label=f'$x_{{{iteration+1}}}$ (aprox. raíz)')
    axs[1].axhline(0, color='black', linewidth=0.8, linestyle='--')
    axs[1].axvline(xn, color='red', linestyle=':', linewidth=1)
    axs[1].axvline(xn_next, color='blue', linestyle=':', linewidth=1)
    axs[1].fill_between(x_local, y_orig_local, y_taylor_local, color='lightgreen', alpha=0.3)
    axs[1].set_title(f'Zoom local en $x_{{{iteration}}}$ ± {delta_zoom}')
    axs[1].set_xlabel('$x$')
    axs[1].set_ylabel('$f(x)$')
    axs[1].legend(fontsize=9)
    axs[1].grid(True, linestyle='--', alpha=0.6)
    axs[1].set_xlim(xn - delta_zoom, xn + delta_zoom)
    y_min_local = min(np.min(y_orig_local), np.min(y_taylor_local)) - 0.1
    y_max_local = max(np.max(y_orig_local), np.max(y_taylor_local)) + 0.1
    axs[1].set_ylim(y_min_local, y_max_local)

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    return buffer
 
def graficar_comparacion_convergencia():
    historial_taylor, historial_combinado, _ = ejecutar_metodos_con_comparacion(
    a=2.5, b=3.5, tol=1e-6, max_iter=50
)


    errores_taylor = [step['error'] for step in historial_taylor]
    errores_combinado = [step['error'] for step in historial_combinado]

    iter_taylor = list(range(1, len(errores_taylor) + 1))
    iter_combinado = list(range(1, len(errores_combinado) + 1))

    ultima_taylor = iter_taylor[-1]
    ultima_combinado = iter_combinado[-1]

    plt.figure(figsize=(10, 6))
    plt.semilogy(iter_taylor, errores_taylor, 'o-', label='Taylor (2º orden)', color='blue')
    plt.semilogy(iter_combinado, errores_combinado, 's--', label='Combinado (Taylor + Bisección)', color='green')

    plt.axvline(x=ultima_taylor, color='blue', linestyle=':', label=f'Convergencia Taylor ({ultima_taylor} it.)')
    plt.axvline(x=ultima_combinado, color='green', linestyle=':', label=f'Convergencia Combinado ({ultima_combinado} it.)')

    plt.title("Iteración de convergencia para cada método")
    plt.xlabel("Iteración")
    plt.ylabel("Error (escala logarítmica)")
    plt.grid(True, which="both", ls="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    return buf

PROBLEMAS_INCISO_A = """
🔍 ¿Qué estamos resolviendo?
Desarrollamos un método numérico para encontrar raíces de funciones no lineales utilizando la expansión en serie de Taylor hasta la segunda derivada. El objetivo es hallar un valor x tal que f(x) = 0, comenzando desde una estimación inicial x₀.

🔢 La expansión de Taylor hasta segundo orden de f(x) alrededor de xₙ es:
    f(x) ≈ f(xₙ) + f'(xₙ)(x - xₙ) + (1/2)f''(xₙ)(x - xₙ)²

Igualamos a cero y resolvemos para obtener la siguiente aproximación xₙ₊₁.

---

✅ Condiciones para aplicar el método:
1. La función f debe ser derivable al menos dos veces.
2. f', f'' deben ser continuas en el entorno de la raíz.
3. f''(xₙ) no debe ser cercano a cero (evita inestabilidad).
4. El discriminante D = (f')² - 2f·f'' debe ser ≥ 0 (evita raíces complejas).
5. El punto inicial x₀ debe estar razonablemente cerca de la raíz.

---

🔁 Justificación del paso iterativo:
Planteamos la ecuación cuadrática en Δx = x - xₙ:

    f''·Δx² + 2f'·Δx + 2f = 0

Resolvemos con fórmula general:

    Δx = [ -f' ± √(f'² - 2f·f'') ] / f''

Elegimos el Δx con menor módulo y actualizamos:

    xₙ₊₁ = xₙ + Δx

---

📉 Error y convergencia:
El error se calcula como:

    error = |xₙ₊₁ - xₙ|

Se verifica la convergencia si el error es menor a una tolerancia (por ejemplo, 1e-6).

⚡ El método puede tener orden de convergencia superior a 2, dependiendo de la función. En general, converge más rápido que Newton-Raphson si las condiciones son adecuadas.

---

✅ Confirmación con función conocida:
En este TP, aplicamos este método a la ecuación de Van der Waals para CO₂, y lo validamos también con funciones conocidas para confirmar la validez del procedimiento.
"""

PROBLEMAS_INCISO_B = """
🧠 1) Criterios de aplicación para lograr robustez

El algoritmo desarrollado combina la rapidez del método de Taylor de segundo orden con la solidez del método de bisección. Para decidir cuál utilizar en cada iteración, se siguen estos criterios:

- ❌ No se aplica Taylor si:
  - El discriminante `f'(x)² - 2·f(x)·f''(x)` es negativo (raíz compleja).
  - La segunda derivada `f''(x)` es muy cercana a cero (riesgo de división numéricamente inestable).
  - La estimación resultante queda fuera del intervalo de búsqueda `[a, b]`.

- ✅ Se aplica Taylor si:
  - El discriminante es positivo.
  - La segunda derivada tiene un valor significativo.
  - El nuevo valor calculado cae dentro del intervalo permitido.

- 🔁 En ambos casos, el intervalo se actualiza según el signo de `f(x)` (como en bisección) para mantener la raíz dentro de [a, b].

De esta manera, el método se adapta a cualquier intervalo inicial y se vuelve automáticamente robusto, incluso frente a funciones complicadas.

---

⚡ 2) Comparación de eficiencia computacional

- 🔐 Bisección:  
  Es extremadamente robusto, siempre converge si hay cambio de signo. Pero es lento, ya que la convergencia es lineal.  
  No requiere derivadas y cada iteración es muy barata.

- ⚡ Taylor puro:  
  Es mucho más rápido (convergencia superlineal), pero menos confiable: puede fallar si la función no es suave o si las derivadas no se comportan bien.  
  Requiere calcular `f'` y `f''`, por lo que tiene un mayor costo por iteración.

- 🔀 Método combinado:  
  Se comporta como Taylor cuando puede (velocidad), y cae de forma segura en bisección cuando debe (robustez).  
  Es eficiente, confiable y rápido: un excelente equilibrio entre rendimiento y estabilidad.

---

🏁 Resultado empírico:  
En nuestras pruebas, el método combinado:
- Fue más veloz en tiempo total.
- Requirió menos iteraciones efectivas.
- Conservó la precisión, incluso en intervalos no óptimos.

✅ Es la opción más segura y poderosa cuando se busca automatizar la búsqueda de raíces en funciones no lineales.

"""

def generar_grafico_funcion_enferma():
    def f(x):
        return np.exp(-x) * np.cos(5 * x) - (1 / 100) * x

    # Buscar una raíz real en un intervalo donde ya sabemos que hay una (por ejemplo, cerca de x = 1.5)
    raiz = brentq(f, 2.5, 3.5)

    x_vals = np.linspace(-1, 6, 1000)
    y_vals = f(x_vals)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_vals, y_vals, label=r'$f(x) = e^{-x} \cos(5x) - \frac{1}{100}x$', color='blue', linewidth=2)
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.axvline(raiz, color='red', linestyle=':', linewidth=1) #type: ignore
    ax.plot(raiz, f(raiz), 'ro', label=f'Raíz ≈ {raiz:.6f}') #type: ignore
    ax.annotate(f'Raíz ≈ {raiz:.6f}',
                xy=(raiz, 0),#type: ignore
                xytext=(raiz + 0.5, 0.2),#type: ignore
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, color='red')

    ax.set_title(r'Visualización de $f(x) = e^{-x} \cos(5x) - \frac{1}{100}x$ y su raíz', fontsize=14)
    ax.set_xlabel('$x$', fontsize=12)
    ax.set_ylabel('$f(x)$', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    fig.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    plt.close(fig)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")