# services/tp6/service_inciso_f.py
import matplotlib.pyplot as plt
import numpy as np
from services.tp6.numerical import save_plot_to_buffer
from services.tp6.core import processor

def get_consigna():
    return "f) En todos los casos aclare la discretización espacial y temporal utilizada. Informe el costo computacional en todos los casos."

def get_console():
    times = processor.get_times()
    
    # Formateo de tabla
    w_inc = 12
    w_time = 18
    sep = "-" * (w_inc + w_time + 3)
    
    out = [
        "\n--- RESUMEN DE COSTO COMPUTACIONAL (Inciso F) ---",
        sep,
        f"{'Inciso':<{w_inc}} | {'Tiempo (s)':<{w_time}}",
        sep
    ]
    
    for k, v in times.items():
        if v == 0: val = "Pendiente"
        elif v < 0.001: val = "< 0.001 s"
        else: val = f"{v:.4f} s"
        
        out.append(f"{'Inciso '+k:<{w_inc}} | {val:<{w_time}}")
        
    out.append(sep)
    
    valid_times = {k: v for k, v in times.items() if v > 0}
    
    if valid_times:
        max_k = max(valid_times, key=valid_times.get)
        max_v = valid_times[max_k]
        out.append(f"\nEl inciso más costoso fue el {max_k} con {max_v:.2f} segundos.")
        if max_k == "B":
            out.append("Esto se debe a la alta no-linealidad (stiffness) del modelo Van Genuchten, que requiere un dt muy pequeño.")
        elif max_k in ["D", "E"]:
            out.append("Esto se debe al tamaño de la malla 2D y la cantidad de nodos.")
    else:
        out.append("\nNo hay datos de ejecución aún. Ejecuta los incisos anteriores.")
    
    return "\n".join(out)

def get_grafico_costos():
    times = processor.get_times()
    labels = list(times.keys())
    values = list(times.values())
    
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6']
    bars = ax.bar(labels, values, color=colors, edgecolor='black', alpha=0.7)
    
    ax.set_title("Comparativa de Costo Computacional por Inciso")
    ax.set_xlabel("Inciso del TP")
    ax.set_ylabel("Tiempo de Ejecución (segundos)")
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + (max(values)*0.01 if max(values)>0 else 0),
                    f'{height:.2f}s', ha='center', va='bottom', fontsize=9, fontweight='bold')
        else:
            ax.text(bar.get_x() + bar.get_width()/2., 0,
                    'N/A', ha='center', va='bottom', fontsize=8, color='gray')

    return save_plot_to_buffer(fig)
 
def get_explicacion():
    return """
    **Análisis de Costo Computacional (Inciso F):**
    
    1. **Inciso A (1D Lineal):** Instantáneo. Pocos nodos ($N \approx 50$) y problema suave.
    
    2. **Inciso B (1D No Lineal):** **El más costoso.**
       - Aunque es 1D, la difusividad $D(\theta)$ cae a casi cero. Esto fuerza al algoritmo a usar un $\Delta t$ diminuto ($\approx 10^{-4}$s) para no divergir. Requiere cientos de miles de pasos de tiempo.
    
    3. **Incisos C, D, E (2D):**
       - Costo intermedio. El número de nodos crece al cuadrado ($N^2$). Una malla de $100 \times 100$ son 10,000 puntos a calcular por paso de tiempo.
       - Sin embargo, como $D$ es constante (o lineal), el paso de tiempo permitido es razonable y terminan rápido (fracción de segundo o pocos segundos).
       
    **Conclusión General:** La no-linealidad fuerte (Caso B) impacta más en el costo que la dimensionalidad (Caso 2D) para estas escalas de problema, debido a las restricciones de estabilidad temporal.
    """