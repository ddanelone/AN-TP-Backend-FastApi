import io
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from io import BytesIO

# Constantes físicas
R = 8.314  # J/(mol·K)
a = 3.592 * 100  # J·L/mol²
b = 0.0427  # L/mol
n = 1  # mol
T = 200.0  # K

temperaturas = [150, 200, 250, 300]
colores = ['blue', 'green', 'orange', 'red']

def generar_grafico_comparativo_gral():
    Vm = np.linspace(0.05, 5, 500)  # Volumen molar en L/mol
    fig, ax = plt.subplots(figsize=(10, 6))

    for T, color in zip(temperaturas, colores):
        P_vdw = (n * R * T) / (Vm - b) - a / Vm**2  # presión en Pa
        Z_vdw = (P_vdw * Vm) / (n * R * T)
        mask = (Vm > b) & (P_vdw > 0) & (Z_vdw > 0)
        ax.plot(P_vdw[mask] / 1e5, Z_vdw[mask], label=f"T = {T} K", color=color)

    ax.axhline(1, color='black', linestyle='dashed', label='Gas Ideal (Z = 1)')
    ax.set_xlabel("Presión (bar)")
    ax.set_ylabel(r"$\frac{PV}{nRT}$")
    ax.set_title("Comportamiento del CO₂: Gas Ideal vs Van der Waals")
    ax.legend(loc='upper right')
    ax.grid(True)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    return buffer

def generar_grafico_comparativo_z():
    P_MPa = np.linspace(0.1, 10, 300)
    P_Pa = P_MPa * 1e6

    fig, ax = plt.subplots(figsize=(10, 6))

    def resolver_vm(P, T):
        def f(Vm):
            return (R * T) / (Vm - b) - a / Vm**2 - P
        Vm_inicial = R * T / P
        try:
            Vm_sol, = fsolve(f, Vm_inicial) # type: ignore
            return Vm_sol if Vm_sol > b else np.nan
        except:
            return np.nan

    for T, color in zip(temperaturas, colores):
        Z_list = []
        for P in P_Pa:
            Vm = resolver_vm(P, T)
            Z = (P * Vm) / (R * T) if not np.isnan(Vm) else np.nan
            Z_list.append(Z)
        ax.plot(P_Pa / 1e6, Z_list, label=f"T = {T} K", color=color)

    ax.axhline(1, color='black', linestyle='dashed', label='Gas Ideal (Z = 1)')
    ax.axvline(5, color='red', linestyle='dotted', linewidth=1, label='P = 5 MPa')
    ax.set_xlabel("Presión (MPa)")
    ax.set_ylabel(r"$Z = \frac{PV}{nRT}$")
    ax.set_title("Factor de Compresibilidad del CO₂ según Van der Waals")
    ax.legend(loc='upper left')
    ax.grid(True)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    return buffer

def generar_grafico_f_vdw():
    # Presiones a comparar
    R = 8.314
    T = 200.0
    a = 0.364
    b = 4.267e-5

    presiones = {
        "P = 5.0 MPa": 5e6,
        "P = 0.5 MPa": 0.5e6
    }

    # Dominio de volumen molar restringido
    v_vals = np.linspace(b * 1.01, 0.005, 1000)

    # Función de Van der Waals
    def f_vdw(v, P):
        return (P + a / v**2) * (v - b) - R * T

    # Crear gráfico
    fig, ax = plt.subplots(figsize=(10, 6))

    for etiqueta, P in presiones.items():
        f_vals = []
        for v in v_vals:
            try:
                f = f_vdw(v, P)
                f_vals.append(f)
            except:
                f_vals.append(np.nan)

        color = 'blue' if P > 1e6 else 'red'
        ax.plot(v_vals, f_vals, label=etiqueta, color=color)

    # Estética del gráfico
    ax.axhline(0, color="gray", linestyle="--")
    ax.axvline(b, color="black", linestyle=":", label=f"b = {b:.2e} m³/mol")
    ax.set_xlim([b * 1.01, 0.005])  # type: ignore
    ax.set_title("f(v) de Van der Waals (CO₂) - Comparación de presiones")
    ax.set_xlabel("Volumen molar v (m³/mol)")
    ax.set_ylabel("f(v)")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    # Guardar imagen en buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf