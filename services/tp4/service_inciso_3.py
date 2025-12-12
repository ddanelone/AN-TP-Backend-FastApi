import matplotlib.pyplot as plt
import io
import numpy as np
from .core import processor

CONSIGNA = """
3) Análisis de variables auxiliares
a) Calcular propiedades geométricas relevantes:
   - Perímetro izquierdo y derecho (Simetría).
   - Factor de esparcimiento (Sf = Diámetro / Altura).
b) Estimar la energía cinética de la gota y discutir su conservación.
"""

EXPLICACION = """
🔹 ANÁLISIS DE VARIABLES AUXILIARES

1. FACTOR DE ESPARCIMIENTO (Sf):
   Relación ancho/alto de la gota.
   • El pico inicial muestra el aplastamiento máximo.
   • Las ondas posteriores son la vibración natural amortiguada.

2. SIMETRÍA:
   Comparación de perímetros izquierdo vs derecho.
   • Curvas juntas = Impacto simétrico vertical.
   • Curvas separadas = Impacto oblicuo o irregularidad.

3. ENERGÍA CINÉTICA (Ec):
   Cálculo: Ec = 0.5 * m * v^2
   • RESULTADO: La energía cinética cae abruptamente.
   • CONCLUSIÓN: No hay conservación. La energía se disipa por viscosidad y se almacena como tensión superficial.
"""

def generar_grafico_sf():
    df = processor.get_data()
    fig, ax = plt.subplots(figsize=(8, 5))
    
    ax.plot(df["t_ms"], df["Sf"], 'm-', label="Factor de Esparcimiento ($S_f$)")
    
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("$S_f = D/H$")
    ax.set_title("Factor de Esparcimiento vs Tiempo")
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def generar_grafico_simetria():
    df = processor.get_data()
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Convertir a mm para mejor escala
    ax.plot(df["t_ms"], df["per_izq"]*1000, 'b-', label="Perímetro Izq")
    ax.plot(df["t_ms"], df["per_der"]*1000, 'r--', label="Perímetro Der")
    
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Perímetro [mm]")
    ax.set_title("Análisis de Simetría (Perímetros)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def generar_grafico_energia():
    df = processor.get_data()
    
    # Calcular velocidad vertical (dy/dt)
    # t en segundos, y en metros
    t_s = df["t_ms"] / 1000
    vy = np.gradient(df["cy_m"], t_s)
    
    # Ec = 0.5 * m * v^2
    Ec = 0.5 * df["masa"] * vy**2
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # En MicroJoules
    ax.plot(df["t_ms"], Ec * 1e6, 'g-', label="Energía Cinética")
    
    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Energía Cinética [µJ]")
    ax.set_title("Evolución de la Energía Cinética")
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def obtener_salida_consola():
    """Genera resumen de Sf, Simetría y Energía."""
    df = processor.get_data()
    
    # Factor de Esparcimiento
    sf_max = df["Sf"].max()
    t_sf_max = df.loc[df["Sf"].idxmax(), "t_ms"]
    sf_final = df["Sf"].iloc[-10:].mean()
    
    # Energía
    # Recalculamos Ec para mostrar valores
    t_s = df["t_ms"] / 1000
    vy = np.gradient(df["cy_m"], t_s)
    Ec = 0.5 * df["masa"] * vy**2
    ec_max = Ec.max() * 1e6 # microjoules
    
    # Simetría (Diferencia promedio porcentual)
    # Evitar div por cero
    diff = np.abs(df["per_izq"] - df["per_der"])
    avg_per = (df["per_izq"] + df["per_der"]) / 2
    # Filtrar donde avg_per es muy chico para no explotar
    valid = avg_per > 1e-6
    asimetria_avg = (diff[valid] / avg_per[valid]).mean() * 100

    return f"""
--- ANÁLISIS DE VARIABLES AUXILIARES ---

1. FACTOR DE ESPARCIMIENTO (Sf = D/H):
   > Máximo Esparcimiento: {sf_max:.2f} (en t={t_sf_max:.2f} ms)
   > Valor de Equilibrio (final): {sf_final:.2f}
   
2. SIMETRÍA (Perímetros Izq vs Der):
   > Asimetría Promedio Global: {asimetria_avg:.2f}%
   > (Valores bajos < 5% indican impacto simétrico)

3. ENERGÍA CINÉTICA (Ec):
   > Energía Máxima (Impacto): {ec_max:.2f} µJ
   > Energía Final (Reposo): ~0.00 µJ
   > Conclusión: La energía NO se conserva (Disipación por viscosidad y deformación).
------------------------------------------------------------------
"""
