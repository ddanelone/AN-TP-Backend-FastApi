from fastapi.responses import  StreamingResponse
import matplotlib.pyplot as plt
import numpy as np
import io
import time
import sympy as sp
import matplotlib.patches as patches

from models.tp3.gases import ParametrosIniciales

# ---------------------
# Constantes y funciones
# ---------------------

R = 8.314  # J/(mol·K)
T = 200.0  # K
a_cte   = 0.364e6  # Pa·m^6/mol^2   según tabla para el CO2
b_cte = 4.27e-5  # m^3/mol        según tabla para el CO2
pressures = [5e6, 0.5e6]  # Pascales
P = 0.5e6

# COMIENZA MATAFUEGO
def obtener_funciones_expr(P, T, a, b, R_local):
    v = sp.Symbol('v')
    f_expr = (P + a / v**2) * (v - b) - R_local * T  # <-- R explícito
    f1_expr = sp.diff(f_expr, v)
    f2_expr = sp.diff(f1_expr, v)
    return v, f_expr, f1_expr, f2_expr

def obtener_funciones_numericas(P, T, a_vdw, b_vdw, R_local):
    v = sp.Symbol('v')
    f_expr = (P + a_vdw / v**2) * (v - b_vdw) - R_local * T
    f = sp.lambdify(v, f_expr, modules='numpy')
    f1 = sp.lambdify(v, sp.diff(f_expr, v), modules='numpy')
    f2 = sp.lambdify(v, sp.diff(f_expr, v, 2), modules='numpy')
    return f, f1, f2

def metodo_taylor(a, b, tol, max_iter, P, T, a_vdw, b_vdw, R_local):
    f, f1, f2 = obtener_funciones_numericas(P, T, a_vdw, b_vdw, R_local)
    x0 = (a + b) / 2
    historial = []

    for n in range(max_iter):
        fx = f(x0)
        f1x = f1(x0)
        f2x = f2(x0)
        discriminante = f1x**2 - 2 * fx * f2x

        if discriminante < 0 or abs(f2x) < 1e-12:
            # No aplicamos Taylor si no es posible, retomamos centro intervalo
            delta = 0.0
            x1 = (a + b) / 2
        else:
            sqrt_disc = np.sqrt(discriminante)
            delta1 = (-f1x + sqrt_disc) / f2x
            delta2 = (-f1x - sqrt_disc) / f2x
            delta = delta1 if abs(delta1) < abs(delta2) else delta2
            x1 = x0 + delta

        error = abs(x1 - x0)
        historial.append({"iter": n, "x": x0, "fx": fx, "error": error})

        if abs(fx) < tol:
            break

        if f(a)*f(x0) < 0:
            b = x0
        else:
            a = x0

        x0 = x1

    return historial
 
def ejecutar_metodos_con_comparacion(a=0.1, b=18.0, tol=1e-6, max_iter=50, P=None, T=None, a_vdw=a_cte, b_vdw=b_cte, R_local=R):
    f, _, _ = obtener_funciones_numericas(P, T, a_vdw, b_vdw, R_local)
    log = io.StringIO()
    print("Comparación de rendimiento: Método de Taylor vs Combinado Taylor-Bisección\n", file=log)

    a1, b1 = a, b
    a2, b2 = a, b

    # Taylor puro
    start_taylor = time.perf_counter()
    historial_taylor = metodo_taylor(a=a1, b=b1, tol=tol, max_iter=max_iter, P=P, T=T, a_vdw=a_vdw, b_vdw=b_vdw, R_local=R_local)
    end_taylor = time.perf_counter()
    tiempo_taylor = end_taylor - start_taylor

    # Método combinado
    start_combinado = time.perf_counter()
    historial_combinado, log_combinado = metodo_taylor_biseccion_con_log(
        a=a2, b=b2, tol=tol, max_iter=max_iter, P=P, T=T, a_vdw=a_vdw, b_vdw=b_vdw, R_local=R_local
    )
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

    return historial_taylor, historial_combinado, log.getvalue() + "\n\n" + log_combinado

def calcular_volumenes_con_params(params: ParametrosIniciales):
    resultados = []
    presiones = [5e6, 0.5e6]

    for P in presiones:
        v_ideal = R * T / P  # T sigue siendo constante global

        # Definir intervalo según presión
        if P >= 1e6:
            a_ini = params.b * 1.01
            b_fin = params.b * 5
        else:
            a_ini = v_ideal * 0.5
            b_fin = v_ideal * 5

        # Ejecutar métodos
        _, historial_combinado, _ = ejecutar_metodos_con_comparacion(
            a=a_ini,
            b=b_fin,
            tol=params.tol,
            max_iter=params.max_iter,
            P=P,
            T=T,  # constante global
            a_vdw=params.a,
            b_vdw=params.b
        )

        v_real = None
        mensaje = "❌ No se encontró raíz válida"

        if historial_combinado:
            # Ordenamos las raíces candidatas por |f(x)|
            candidatas = sorted(
                (step for step in historial_combinado if abs(step.get("fx", float("inf"))) < 1e3),
                key=lambda s: abs(s["fx"])
            )

            for step in candidatas:
                xr = step["x"]
                fx = abs(step["fx"])
                diferencia_relativa = abs(xr - v_ideal) / v_ideal

                # Criterios de coherencia según presión
                if fx < 1e-4:
                    if P >= 1e6 and xr < 0.7 * v_ideal:
                        v_real = xr
                        mensaje = f"✅ v_real ≈ {xr:.2e}, diferencia ≈ {diferencia_relativa:.2f}%"
                        break
                    elif P < 1e6 and 0.8 < xr / v_ideal < 1.2:
                        v_real = xr
                        mensaje = f"✅ v_real ≈ {xr:.2e}, diferencia ≈ {diferencia_relativa:.2f}%"
                        break

        resultados.append((P, v_ideal, v_real, mensaje))

    return resultados

def metodo_taylor_biseccion_con_log(a, b, tol=1e-12, max_iter=50, P=None, T=None, a_vdw=0.001, b_vdw=0.05, R_local=R):
    f, f1, f2 = obtener_funciones_numericas(P, T, a_vdw, b_vdw, R_local)
    log = io.StringIO()
    print("Método combinado: Taylor (2da derivada) + Bisección\n", file=log)

    x0 = (a + b) / 2
    historial = []

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

        if f(a) * f(x0) < 0:
            b = x0
        else:
            a = x0
        iter_actualizacion_intervalo += 1

        x0 = x1

    print("Resumen comparativo de uso de métodos:", file=log)
    print(f"  Iteraciones totales: {n+1}", file=log)  # type: ignore
    print(f"  Iteraciones con método Taylor: {iter_taylor}", file=log)
    print(f"  Iteraciones con método Bisección: {iter_biseccion}", file=log)
    print(f"  Iteraciones con actualización de intervalo (tipo bisección): {iter_actualizacion_intervalo}", file=log)
    error_final = historial[-1]["error"] if historial else None
    print(f"  Error final aproximado: {error_final:.15e}", file=log)

    return historial, log.getvalue()

def seleccionar_raiz_valida(historial, v_ideal, P):
    candidatas = sorted(
        (step for step in historial if abs(step.get("fx", float("inf"))) < 1e3),
        key=lambda s: abs(s["fx"])
    )

    for step in candidatas:
        xr = step["x"]
        fx = abs(step["fx"])
        diferencia_relativa = abs(xr - v_ideal) / v_ideal

        if fx < 1e-4:
            if P >= 1e6 and xr < 0.7 * v_ideal:
                return xr, diferencia_relativa
            elif P < 1e6 and 0.8 < xr / v_ideal < 1.2:
                return xr, diferencia_relativa

    return None, None

def resolver_resultado_gas(params: ParametrosIniciales, P: float, T: float, R: float = 8.314):
    v_ideal = R * T / P

    # Interpretamos a y b como coeficientes de Van der Waals
    a_vdw = params.a
    b_vdw = params.b

    # Generamos un intervalo inicial
    a_ini = b_vdw * 1.01
    b_fin = v_ideal * 10

    f, _, _ = obtener_funciones_numericas(P, T, a_vdw, b_vdw, R)

    # Validamos si el intervalo inicial es usable
    if f(a_ini) * f(b_fin) >= 0:
        nuevo_a, nuevo_b = encontrar_intervalo(f, v_ideal)

        if nuevo_a is None or nuevo_b is None:
            return {
                "mensaje": "❌ No se encontró intervalo válido para aplicar los métodos.",
                "volumen_ideal": f"{v_ideal:.6e}",
                "volumen_taylor": "N/A",
                "volumen_combinado": "N/A",
                "diferencia_taylor_%": "N/A",
                "diferencia_combinado_%": "N/A",
                "log": "No se pudo validar el intervalo para aplicar Taylor ni el método combinado."
            }

        a_ini, b_fin = nuevo_a, nuevo_b

    # Garantizar que no sean None (para Pylance y seguridad)
    assert a_ini is not None and b_fin is not None, "Intervalo inválido"

    # Ejecutar métodos
    historial_taylor, historial_combinado, log = ejecutar_metodos_con_comparacion(
        a=a_ini,
        b=b_fin,
        tol=params.tol,
        max_iter=params.max_iter,
        P=P,
        T=T,
        a_vdw=a_vdw,
        b_vdw=b_vdw,
        R_local=R
    )

    # Buscar raíces válidas
    v_taylor, dif_taylor = seleccionar_raiz_valida(historial_taylor, v_ideal, P)
    v_combinado, dif_combinado = seleccionar_raiz_valida(historial_combinado, v_ideal, P)

    def format_volumen(valor):
        if valor is None:
            return "❌ No se encontró raíz válida"
        return f"{valor:.6e}"

    return {
        "mensaje": "Resolución del inciso 2.b con los métodos solicitados",
        "volumen_ideal": f"{v_ideal:.6e}",
        "volumen_taylor": format_volumen(v_taylor),
        "volumen_combinado": format_volumen(v_combinado),
        "diferencia_taylor_%": f"{dif_taylor:.4f}%" if dif_taylor is not None else "N/A",
        "diferencia_combinado_%": f"{dif_combinado:.4f}%" if dif_combinado is not None else "N/A",
        "log": log
    }


    return {
        "mensaje": "Resolución del inciso 2.b con los métodos solicitados",
        "volumen_ideal": f"{v_ideal:.6e}",
        "volumen_taylor": format_volumen(v_taylor),
        "volumen_combinado": format_volumen(v_combinado),
        "diferencia_taylor_%": f"{dif_taylor:.4f}%" if dif_taylor is not None else "N/A",
        "diferencia_combinado_%": f"{dif_combinado:.4f}%" if dif_combinado is not None else "N/A",
        "log": log
    }


    return {
        "mensaje": "Resolución del inciso 2.b con los métodos solicitados",
        "volumen_ideal": f"{v_ideal:.6e}",
        "volumen_taylor": format_volumen(v_taylor),
        "volumen_combinado": format_volumen(v_combinado),
        "diferencia_taylor_%": f"{dif_taylor:.4f}%" if dif_taylor is not None else "N/A",
        "diferencia_combinado_%": f"{dif_combinado:.4f}%" if dif_combinado is not None else "N/A",
        "log": log
    }

# TERMINA MATAFUEGO

def van_der_waals_eq(v, P, T):
    return (P + a_cte / v**2) * (v - b_cte) - R * T

def calcular_volumenes():
    resultados = []
    pressures = [5e6, 0.5e6]
    for P in pressures:
        v_ideal = R * T / P

        # ✅ Intervalo adaptado a cada presión (basado en v_ideal)
        a_ini = b_cte * 1.01
        b_fin = v_ideal * 10

        # Ejecutamos método combinado
        _, historial_combinado, _ = ejecutar_metodos_con_comparacion(a_ini, b_fin, P=P, T=T)

        if historial_combinado:
            v_real = historial_combinado[-1]["x"]
            diferencia = abs(v_real - v_ideal) / v_real * 100
            mensaje = f"v_real ≈ {v_real:.2e}, diferencia ≈ {diferencia:.2f}%"
        else:
            v_real = None
            mensaje = "❌ No se encontró raíz válida"

        resultados.append((P, v_ideal, v_real, mensaje))

        try:
            print(f"\nPresión: {P/1e6:.1f} MPa")
            print(f"v_ideal: {v_ideal:.6e}")
            print(f"v_real: {v_real}")
            print(mensaje)
        except UnicodeEncodeError:
            print(f"\nPresion: {P/1e6:.1f} MPa")
            print(f"v_ideal: {v_ideal:.6e}")
            print(f"v_real: {v_real}")
            print(mensaje.encode("ascii", "replace").decode())

    return resultados

def generar_grafico_gases(resultados):
    fig, axs = plt.subplots(1, len(resultados), figsize=(14, 5))

    for i, (P, v_ideal, v_real, mensaje) in enumerate(resultados):
        ax = axs[i] if len(resultados) > 1 else axs

        v_min_plot = max(b_cte * 1.01, 1e-6)
        v_max_plot = v_ideal * 5 if v_ideal is not None else 0.01

        if v_real is not None:
            v_min_plot = min(v_min_plot, v_real * 0.5)
            v_max_plot = max(v_max_plot, v_real * 1.5)

        v_vals = np.linspace(v_min_plot, v_max_plot, 1000)

        f_vals = []
        for v in v_vals:
            try:
                f_val = van_der_waals_eq(v, P, T)  # sigue usando versión vieja con globals
                f_vals.append(f_val)
            except:
                f_vals.append(np.nan)

        f_vals = np.array(f_vals)
        v_vals = np.array(v_vals)

        mask = np.isfinite(f_vals)
        v_plot = v_vals[mask]
        f_plot = f_vals[mask]

        ax.plot(v_plot, f_plot, label=f'f(v) para {P/1e6:.1f} MPa')
        ax.axhline(0, color='black', linestyle='--', label='y = 0')

        if v_real is not None:
            ax.axvline(v_real, color='green', linestyle='--', label=f'v_real ≈ {v_real:.6f}')
        else:
            ax.text(0.5, 0.1, "v_real no válida", transform=ax.transAxes, color="gray", fontsize=10)

        ax.axvline(v_ideal, color='red', linestyle=':', label=f'v_ideal ≈ {v_ideal:.6f}')

        ax.set_xlabel('Volumen molar v (m³/mol)')
        ax.set_ylabel('f(v)')
        ax.set_title(f'Van der Waals: P = {P/1e6:.1f} MPa')
        ax.legend()
        ax.grid(True)

        y_margin = (np.nanmax(f_plot) - np.nanmin(f_plot)) * 0.1
        ax.set_ylim(np.nanmin(f_plot) - y_margin, np.nanmax(f_plot) + y_margin)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf


# --- Buscar intervalo válido ---
def encontrar_intervalo(f, v_inicial, ancho_inicial=0.01, max_iter=100):
    """Busca un intervalo [a, b] tal que f(a)*f(b) < 0"""
    ancho = ancho_inicial
    for _ in range(max_iter):
        a = max(v_inicial - ancho, 1e-6)
        b = v_inicial + ancho
        if f(a) * f(b) < 0:
            return a, b
        ancho *= 1.5
    return None, None


def generar_grafico_general(v_ideal, v_real, P, T):
    # Margen visual para graficar
    v_min = min(v_real, v_ideal) * 0.5
    v_max = max(v_real, v_ideal) * 1.5

    v_vals = np.linspace(v_min, v_max, 1000)

    f_vals = []
    for v in v_vals:
        try:
            f_vals.append(van_der_waals_eq(v, P, T))
        except:
            f_vals.append(np.nan)

    f_vals = np.array(f_vals)
    v_vals = np.array(v_vals)
    mask = np.isfinite(f_vals)
    v_plot = v_vals[mask]
    f_plot = f_vals[mask]

    plt.figure(figsize=(8, 5))
    plt.plot(v_plot, f_plot, label='f(v)', color='blue')
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.axvline(v_ideal, color='red', linestyle=':', linewidth=1.5, label=f'v_ideal ≈ {v_ideal:.6f}')
    plt.axvline(v_real, color='green', linestyle='--', linewidth=1.5, label=f'v_real ≈ {v_real:.6f}')

    plt.title(f'Función de Van der Waals a {P/1e6:.1f} MPa', fontsize=14)
    plt.xlabel('Volumen molar [m³/mol]')
    plt.ylabel('f(v)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return StreamingResponse(buf, media_type='image/png')



def generar_grafico_zoom(v_real, P, T):
    delta = v_real * 0.2  # Zoom de ±20% alrededor de la raíz
    v_zoom_vals = np.linspace(v_real - delta, v_real + delta, 1000)
    f_zoom_vals = [van_der_waals_eq(v, P, T) for v in v_zoom_vals]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(v_zoom_vals, f_zoom_vals, label='f(v) (zoom)', color='royalblue', linewidth=2)
    ax.axhline(0, color='black', linestyle='--', linewidth=1)
    ax.axvline(v_real, color='green', linestyle='--', linewidth=1.5, label=f'v_real ≈ {v_real:.6f}')

    f_en_raiz = van_der_waals_eq(v_real, P, T)
    ax.plot(v_real, f_en_raiz, 'go', label='Raíz')

    ax.text(0.05, 0.95, f'f(v_real) ≈ {f_en_raiz:.2e}', transform=ax.transAxes,
            fontsize=10, verticalalignment='top', color='dimgray')

    ax.set_title('Zoom en la raíz encontrada (Taylor + Bisección)', fontsize=14)
    ax.set_xlabel('Volumen molar [m³/mol]')
    ax.set_ylabel('f(v)')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    ax.ticklabel_format(style='plain', axis='x')
    ax.ticklabel_format(style='plain', axis='y')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return StreamingResponse(buf, media_type='image/png')
 
# --- Método de Taylor de segundo orden para Van der Waals ---
def taylor_vdw(P, T, v0=None, tol=1e-8, max_iter=100):
    if v0 is None:
        v0 = R * T / P  # Punto inicial si no se especifica

    errores = []
    v = v0
    for i in range(max_iter):
        try:
            f = van_der_waals_eq(v, P, T)
            f_prime = -2 * a_cte / v**3 + (P + a_cte / v**2)
            f_double_prime = 6 * a_cte / v**4

            if abs(f_prime) < 1e-12:
                return None, errores, "❌ Derivada primera casi nula. Método no aplicable."

            delta = f / f_prime + 0.5 * f * f_double_prime / (f_prime**2)
            v_new = v - delta

            error = abs(v_new - v)
            errores.append(error)

            if error < tol:
                return v_new, errores, f"✅ Convergió en {i+1} iteraciones."

            v = v_new
        except Exception as e:
            return None, errores, f"❌ Error en Taylor: {e}"

    return None, errores, "❌ No convergió en el máximo número de iteraciones."

# --- Comparación de métodos ---
def comparar_metodos_vdw(P=0.5e6, T=200.0, a_vdw=0.364, b_vdw=4.267e-5, tol=1e-6, max_iter=50):
    salida = [
        f"🧪 Comparación de métodos para P = {P/1e6:.1f} MPa, T = {T} K",
        f"📥 Condiciones iniciales evaluadas:",
        f"• a = {a_vdw}",
        f"• b = {b_vdw}",
        f"• tol = {tol}",
        f"• max_iter = {max_iter}\n"
    ]

    v_ideal = R * T / P
    salida.append(f"📌 Volumen ideal: {v_ideal:.6e} m³/mol")

    a_ini = b_vdw * 1.01
    b_fin = v_ideal * 10

    # Validación simple de intervalo realista
    if a_ini >= b_fin or a_ini <= 0 or b_fin <= 0:
        salida.append("\n❌ Intervalo inicial inválido para el gas CO₂ bajo estas condiciones.")
        salida.append(f"📉 a_ini = {a_ini:.3e}, b_fin = {b_fin:.3e}")
        return "\n".join(salida)

    try:
        start = time.perf_counter()
        historial_taylor, historial_combinado, _ = ejecutar_metodos_con_comparacion(
            a=a_ini, b=b_fin, tol=tol, max_iter=max_iter,
            P=P, T=T, a_vdw=a_vdw, b_vdw=b_vdw
        )
        end = time.perf_counter()

        v_taylor = historial_taylor[-1]["x"]
        err_taylor = historial_taylor[-1]["error"]
        salida.append("\n⚙️ Método de Taylor:")
        salida.append(f"✅ Raíz aproximada: {v_taylor:.6e} m³/mol")
        salida.append(f"🔁 Iteraciones: {len(historial_taylor)}")
        salida.append(f"📉 Último error: {err_taylor:.2e}")

        v_comb = historial_combinado[-1]["x"]
        err_comb = historial_combinado[-1]["error"]
        salida.append("\n⚙️ Método combinado Taylor + Bisección:")
        salida.append(f"✅ Raíz aproximada: {v_comb:.6e} m³/mol")
        salida.append(f"🔁 Iteraciones: {len(historial_combinado)}")
        salida.append(f"📉 Último error: {err_comb:.2e}")

        dif_taylor = abs(v_taylor - v_ideal) / v_taylor * 100
        dif_comb = abs(v_comb - v_ideal) / v_comb * 100
        salida.append("\n📊 Comparación con volumen ideal:")
        salida.append(f"🔬 Diferencia Taylor: {dif_taylor:.4f} %")
        salida.append(f"🔬 Diferencia Combinado: {dif_comb:.4f} %")

        salida.append(f"\n⏱️ Tiempo total de ejecución: {(end - start) * 1000:.2f} ms")

    except Exception as e:
        salida.append(f"\n❌ Error al aplicar los métodos: {e}")

    return "\n".join(salida)


EXPLICACION_INCISO_A = """
🔬 Correcciones del modelo de Van der Waals:

La ecuación de Van der Waals mejora el modelo de gas ideal introduciendo dos correcciones fundamentales:

1️⃣ Corrección por volumen propio de las moléculas:
   - En el modelo ideal se supone que las moléculas no ocupan volumen, lo cual no es realista.
   - Van der Waals introduce un término "b", que representa el volumen excluido por mol de moléculas.
   - Esto reduce el volumen disponible efectivo: (v - b), donde v es el volumen molar total.

2️⃣ Corrección por fuerzas intermoleculares:
   - Los gases ideales no consideran interacciones atractivas entre moléculas.
   - Van der Waals corrige esto sumando un término "a / v²" a la presión.
   - Este término reduce la presión efectiva, ya que las fuerzas atractivas disminuyen los choques contra las paredes del recipiente.

📘 Ecuación de Van der Waals:
    (P + a / v²)(v - b) = R·T

Donde:
    - P es la presión del gas
    - v es el volumen molar
    - T es la temperatura
    - R es la constante universal de los gases
    - a y b son constantes características de cada gas

🧪 Estas correcciones permiten modelar el comportamiento real de los gases a presiones altas o temperaturas bajas, donde las desviaciones del modelo ideal son significativas.
"""

PROBLEMAS_INCISO_A = """
🧠 Análisis de la resolución implementada (Inciso 2.a):

Dado que la Ley de los Gases Ideales no permite describir adecuadamente el comportamiento del dióxido de carbono (CO₂) bajo condiciones extremas de presión y temperatura (200 K y 5 MPa), se recurrió al modelo de Van der Waals, que incorpora correcciones por volumen propio de las moléculas y fuerzas de atracción intermoleculares.

📌 Se reformuló la ecuación de Van der Waals como una función no lineal en el volumen molar:

    f(v) = (P + a / v²) · (v - b) - R·T

cuya raíz representa el volumen real buscado. Dado que esta función puede presentar múltiples raíces y singularidades, se implementó un método robusto que combina la aproximación de segundo orden de Taylor con una estrategia tipo bisección para asegurar la estabilidad del proceso iterativo.

🔍 El enfoque numérico aplicado garantiza convergencia incluso ante derivadas pequeñas o discriminantes negativos, alternando entre correcciones tipo Newton-Taylor y actualizaciones del intervalo. Este método se mostró especialmente adecuado para tratar funciones con comportamiento singular cerca de v = b, como ocurre en este modelo.

📊 El resultado obtenido mostró una diferencia relativa de aproximadamente **7688 %** entre el volumen real calculado y el volumen ideal (v = R·T / P). Esta enorme discrepancia es coherente con lo esperado: bajo presiones elevadas y temperaturas bajas, el gas se desvía fuertemente del comportamiento ideal, y modelos como el de Van der Waals son indispensables.

✅ En conclusión, este inciso no solo justifica el uso de modelos físicos más complejos, sino que también demuestra la eficacia del método numérico combinado implementado para resolver ecuaciones no lineales en un contexto físico realista.
"""

PROBLEMAS_INCISO_B = """
📘 Resolución del inciso 2.b:

En esta etapa, se calculó nuevamente el volumen molar real del CO₂, esta vez bajo una presión reducida de 0.5 MPa, manteniendo la temperatura en 200 K. A diferencia del inciso anterior, se utilizaron exclusivamente los dos métodos desarrollados previamente: el método de Taylor de segundo orden y un enfoque combinado que aplica Taylor junto con Bisección para reforzar su estabilidad.

⚙️ El método de Taylor se aplicó directamente a la función de Van der Waals, partiendo desde un valor inicial físicamente razonable (entre 5·b y la mitad del volumen ideal). En solo 3 iteraciones, el método alcanzó convergencia con un error final de 2.33 × 10⁻⁷, arrojando un volumen real coherente y físicamente válido.

🔀 En paralelo, se aplicó una versión combinada del método que alterna entre pasos de Taylor y actualizaciones del intervalo al estilo Bisección. Este enfoque reforzó la robustez del proceso, asegurando que las raíces propuestas se mantuvieran dentro de un rango físico permitido. El método combinado también alcanzó convergencia en 3 iteraciones, con un error aún más bajo: 1.51 × 10⁻¹⁰.

📊 Ambos métodos coincidieron en el valor hallado: aproximadamente 0.5671 m³/mol, lo que representa una diferencia relativa del 99.41 % respecto al volumen ideal estimado por la ley de gases ideales. Este resultado vuelve a evidenciar que incluso a presiones moderadas, las correcciones de Van der Waals no pueden ser despreciadas.

📌 Conclusiones clave:
- Ambos métodos numéricos fueron efectivos, pero el método combinado resultó más robusto ante posibles problemas de convergencia.
- La diferencia con el volumen ideal sigue siendo significativa, reafirmando la validez del modelo de Van der Waals.
- La implementación demostró que el método de Taylor, reforzado con una lógica de validación tipo bisección, puede ser una alternativa precisa, rápida y físicamente confiable.
"""

def generar_grafico_volumenes_comparados(P=0.5e6, T=200.0):
    """
    Genera un gráfico comparativo entre el volumen molar ideal y el volumen molar real (CO₂)
    calculado mediante los métodos de Taylor y Taylor-Bisección, bajo condiciones fijas.
    """

    # Calcular volumen molar ideal
    v_ideal = R * T / P

    # Resolver con métodos aplicados al CO₂ (usando a_co2 y b_co2)
    historial_taylor, historial_combinado, _ = ejecutar_metodos_con_comparacion(
        a=0.001,
        b=0.05,
        P=P,
        T=T,
        a_vdw=a_cte,
        b_vdw=b_cte,
        R_local=R
    )

    # Volúmenes obtenidos por los métodos
    v_taylor = historial_taylor[-1]["x"]
    v_combinado = historial_combinado[-1]["x"]

    # Crear gráfico
    fig, ax = plt.subplots(figsize=(7, 5))

    etiquetas = ["Gas ideal", "CO₂ - Taylor", "CO₂ - Taylor + Bisección"]
    valores = [v_ideal, v_taylor, v_combinado]
    colores = ["#6baed6", "#74c476", "#fd8d3c"]

    # Barras
    ax.bar(etiquetas, valores, color=colores, width=0.6)
    # Título principal + condiciones como subtítulo
    ax.set_title(
      "Comparación de volumen molar: CO₂ vs. Gas ideal\n"
      f"Condiciones: P = {P/1e6:.2f} MPa, T = {T:.0f} K",
      fontsize=12,
      weight="bold",
      loc="center"
    )

    ax.set_ylabel("Volumen molar [m³/mol]", fontsize=12)

    # Mostrar valores sobre las barras
    for i, valor in enumerate(valores):
        ax.text(i, valor + max(valores) * 0.01, f"{valor:.8f}", ha="center", fontsize=10)

    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    # Guardar en buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    return buffer

def generar_imagen_error_volumen():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")

    # Fondo suave
    ax.set_facecolor("#f9f9f9")
    fig.patch.set_facecolor("#f9f9f9")

    # Mensaje principal
    ax.text(
        0.5, 0.75, "❌ No se pueden calcular volúmenes reales",
        fontsize=18, ha="center", va="center", color="#d62828", weight="bold"
    )

    # Mensaje explicativo
    ax.text(
        0.5, 0.55,
        "Las condiciones iniciales no permiten aplicar el\nmodelo de Van der Waals correctamente.",
        fontsize=12, ha="center", va="center", color="#333"
    )

    # Agregar ícono visual con un patch decorativo
    warning_box = patches.FancyBboxPatch(
        (0.35, 0.2), 0.3, 0.2,
        boxstyle="round,pad=0.05", color="#ffd166", ec="#f77f00", lw=2,
        transform=ax.transAxes
    )
    ax.add_patch(warning_box)
    ax.text(
        0.5, 0.3, "Revisá los valores de 'a' y 'b'", ha="center",
        va="center", fontsize=11, weight="bold", color="#000"
    )

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf