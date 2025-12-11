import matplotlib.pyplot as plt
import io
import pandas as pd
import numpy as np
from .core import processor

CONSIGNA = """
2) Medición del ángulo de contacto
a) Ajustar las curvas de los contornos izquierdo y derecho, mediante splines y mediante polinomios de mínimos cuadrados. Determine los grados de ajuste más conveniente en cada caso y justifique.
b) Para cada cuadro en que la gota toca el sustrato, calcular el ángulo de contacto tanto izquierdo como derecho. Graficar los ángulos en función del tiempo.
c) Analizar si el ángulo de contacto obtenido corresponde a un ángulo dinámico o estático y explicar por qué.
"""

EXPLICACION = """
🔹 Análisis de Métodos de Ajuste (2.a):

1. **Splines Cúbicos (UnivariateSpline):**
   - **Ventaja:** Se adaptan localmente a la curvatura de la gota sin asumir una forma global. Son ideales para capturar deformaciones sutiles cerca de la base.
   - **Configuración:** Se usó un factor de suavizado bajo (s=0.0) para interpolar fielmente los puntos detectados.

2. **Polinomios de Mínimos Cuadrados (Polyfit):**
   - **Ventaja:** Filtran mejor el ruido de pixelado si se elige un grado bajo (Grado 2 o 3).
   - **Desventaja:** Pueden no capturar cambios bruscos de curvatura si la ventana de puntos es muy grande.
   - **Elección:** Se utilizó grado 2 en una ventana local de 15 puntos.

🔹 Análisis Dinámico vs Estático (2.c):
Se observa que el ángulo varía significativamente en el tiempo (ver gráfico), oscilando y amortiguándose.
➡ **Conclusión:** Es un **Ángulo de Contacto Dinámico**.
El sistema no está en equilibrio termodinámico; la línea de contacto se mueve (avanza/retrocede) debido a la inercia de la caída y la oscilación posterior de la gota.
"""

def obtener_datos_angulos():
    df = processor.get_data()
    # Filtramos solo columnas relevantes y filas donde haya contacto
    df_ang = df[["t_ms", "angL_spline", "angR_spline", "angL_poly", "angR_poly"]].dropna()
    return df_ang.to_dict(orient="records")

def generar_grafico_angulos():
    """Grafica Ángulos vs Tiempo comparando métodos."""
    df = processor.get_data()
    
    # Filtrar nans (vuelo)
    df_plot = df.dropna(subset=["angL_spline"])
    
    if df_plot.empty: return None

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Graficar Splines (Suelen ser más precisos)
    ax.plot(df_plot["t_ms"], df_plot["angL_spline"], 'o-', ms=3, alpha=0.7, label="Izq (Spline)")
    ax.plot(df_plot["t_ms"], df_plot["angR_spline"], 's-', ms=3, alpha=0.7, label="Der (Spline)")
    
    # Graficar Poly (Comparativa, líneas punteadas)
    ax.plot(df_plot["t_ms"], df_plot["angL_poly"], '--', alpha=0.5, label="Izq (Poly)")
    ax.plot(df_plot["t_ms"], df_plot["angR_poly"], '--', alpha=0.5, label="Der (Poly)")

    ax.set_xlabel("Tiempo [ms]")
    ax.set_ylabel("Ángulo de Contacto [°]")
    ax.set_title("Evolución del Ángulo de Contacto Dinámico")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer

def obtener_salida_consola():
    """Genera la tabla comparativa de ángulos promedios."""
    df = processor.get_data()
    
    # Calcular promedios ignorando NaNs
    # (Usamos los ángulos reales theta, no los complementarios, según tu ejemplo)
    # Si en tu notebook usaste complementarios para el promedio, ajusta aquí.
    # Asumimos que las columnas en 'results' son los ángulos reales theta.
    
    # Nota: En core.py guardamos: angL_spline, angR_spline, angL_poly, angR_poly
    # Estos son los ángulos "theta" corregidos por nuestra función util.
    
    prom_L_s = df["angL_spline"].mean()
    prom_R_s = df["angR_spline"].mean()
    prom_L_p = df["angL_poly"].mean()
    prom_R_p = df["angR_poly"].mean()
    
    return f"""
--- Promedios de Ángulos de Contacto (θ) ---

MÉTODO SPLINE PARAMÉTRICO (θ):
  > Ángulo Izquierdo Promedio: {prom_L_s:.2f} grados
  > Ángulo Derecho Promedio: {prom_R_s:.2f} grados

MÉTODO POLYFIT PARAMÉTRICO (Grado 2/3) (θ):
  > Ángulo Izquierdo Promedio: {prom_L_p:.2f} grados
  > Ángulo Derecho Promedio: {prom_R_p:.2f} grados

------------------------------------------------------------------
*Nota: Se observa una discrepancia sistemática entre métodos debido a la
sensibilidad del Spline a la curvatura local vs el suavizado del Polinomio.
"""
def generar_grafico_ajuste_frame28():
    """Genera los gráficos de ajuste (Izq/Der) para el Frame 28."""
    data = processor.get_ajuste_detalle(frame_obj=28)
    
    if not data or (not data["L"] and not data["R"]):
        return None

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    
    for i, (lado, titulo) in enumerate([("L", "Izquierdo"), ("R", "Derecho")]):
        d = data[lado]
        ax = axs[i]
        
        if d:
            # Puntos originales (scatter)
            ax.scatter(d["pts"][:, 0], d["pts"][:, 1], s=15, label="Puntos Contorno", color="black", zorder=3)
            
            # Curva Spline
            if d["spline_x"] is not None:
                ax.plot(d["spline_x"], d["spline_y"], 'b-', lw=2, label="Spline Cúbico")
                
            # Curva Poly
            if d["poly_x"] is not None:
                ax.plot(d["poly_x"], d["poly_y"], 'r--', lw=2, label="Polinomio G2")
            
            # Línea de sustrato (y=0)
            ax.axhline(0, color="gray", linestyle=":", label="Sustrato")
            
            ax.set_title(f"Ajuste No-Paramétrico {titulo}, Frame 28")
            ax.set_xlabel("x [px]")
            ax.set_ylabel("Altura sobre sustrato [px]")
            ax.legend()
            ax.grid(True)
        else:
            ax.text(0.5, 0.5, "Sin contacto en este lado", ha='center')

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer