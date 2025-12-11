
EXPLICACION_INCISO_2 = """
🔬 Transformada de Fourier aplicada a señales EEG:

La Transformada de Fourier (FFT) permite descomponer una señal en sus componentes de frecuencia. En el contexto del EEG, esta herramienta es clave para identificar en qué bandas cerebrales se concentra la energía de la señal.

✅ Diferencias esperadas entre señales:
- **Sana:** espectro más regular y energía predominante en la banda alfa (8–13 Hz).
- **Interictal:** mayor dispersión espectral, presencia de componentes en theta (4–8 Hz) o incluso delta (0.5–4 Hz).
- **Convulsiva:** espectro caótico con actividad intensa y amplia distribución, pérdida de concentración en bandas típicas.

📈 Información adicional que ofrece la FFT:
- Permite identificar la **energía dominante** en cada banda.
- Muestra **activaciones anómalas** que no son visibles a simple vista en el dominio del tiempo.
- Facilita la detección de patrones repetitivos, armonías o picos inusuales.

💡 Mientras que en el tiempo solo vemos la amplitud en función de los segundos, la FFT revela el "contenido escondido" en el dominio de las frecuencias.
"""

PROBLEMAS_INCISO_2 = """
📘 Resolución del TP1 - Inciso 2: Análisis espectral mediante FFT

En este punto se reutilizaron las señales EEG previamente filtradas y se aplicó la Transformada Rápida de Fourier (FFT) a cada una. Los espectros obtenidos permitieron estudiar cómo varía el contenido frecuencial según el estado cerebral del paciente.

🔹 Señales utilizadas:
- **Señal 1 (sana):** espectro con picos definidos en alfa.
- **Señal 2 (interictal):** distribución espectral más difusa, sin picos bien definidos.
- **Señal 3 (convulsiva):** gran cantidad de componentes distribuidos en múltiples bandas.

🔍 Problemáticas abordadas:
- Se trabajó con señales discretas y de duración limitada, lo que implica resolución espectral restringida.
- Se aplicó una frecuencia de corte en 40 Hz para enfocarnos en las bandas clínicas más relevantes.
- Se compararon los resultados espectrales con las representaciones temporales para confirmar los patrones visuales.

✅ Conclusión:
La FFT aporta una dimensión adicional al análisis EEG, revelando información que el dominio del tiempo no permite observar directamente. Esto la convierte en una herramienta fundamental en el diagnóstico de epilepsia.
"""

CONSIGNA2 = """
2. Aplicar la transformada de Fourier a cada una de las señales. ¿Qué diferencias esperas encontrar en el
espectro de frecuencias de una señal sana frente a una señal interictal o durante la crisis epiléptica? ¿Qué
información adicional proporciona la FFT sobre la señal que no se puede obtener fácilmente en el dominio
del tiempo?
"""