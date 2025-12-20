# Numerical Analysis Engine:

FastAPI BackendEste repositorio contiene el núcleo de procesamiento computacional desarrollado para la resolución de 6 Trabajos Prácticos de la cátedra de Análisis Numérico de la UTN FRSF11. El motor, construido íntegramente en Python con FastAPI, implementa algoritmos avanzados que me valieron la invitación para presentar este trabajo en el Congreso MECOM 2026 (Asociación Argentina de Mecánica Computacional).

# Propósito y Alcance

El sistema expone una API robusta para ejecutar simulaciones matemáticas, procesamiento de señales y análisis de imágenes, transformando modelos teóricos en soluciones computacionales eficientes.

# Stack TecnológicoFramework:

FastAPI (Backend de alto rendimiento con validación mediante Pydantic).Cómputo Científico: NumPy, SciPy (Integración, EDOs, FFT).Procesamiento de Imágenes: OpenCV / ImageJ (Detección de contornos y segmentación).Documentación de API: Swagger / OpenAPI integrada.

# Módulos de Análisis (6 TPs)

1. Procesamiento de Señales EEG (Epilepsia)Análisis de la actividad eléctrica cerebral para diferenciar etapas de epilepsia (sano, interictal, convulsión)2.Técnicas: Transformada Rápida de Fourier (FFT), filtros pasa bajos y autocorrelación para identificar patrones repetitivos y regularidad estructural

2. Esteganografía Digital (Criptografía Visual)Ocultamiento de información mediante el método LSB (Least Significant Bit) y la Transformada de Fourier 2D (TF2D). Desafío: Codificación de mensajes en los planos de frecuencia para garantizar la invisibilidad y robustez de la información cifrada5.

3. Raíces No Lineales y Gases RealesResolución de ecuaciones no lineales utilizando expansión de la Serie de Taylor hasta la segunda derivada6.Aplicación: Cálculo del volumen molar del dióxido de carbono ($CO_{2}$) bajo condiciones extremas de presión (5 MPa) mediante la ecuación de Van der Waals

4. Visión Artificial: Ángulo de ContactoAnálisis de imágenes de una gota cayendo sobre un sustrato para medir mojado y capilaridad8.Técnicas: Segmentación, detección de bordes y ajuste de contornos mediante Splines y polinomios de mínimos cuadrados

5. Dinámica de Spreading e Integración NuméricaCálculo de volumen y superficie lateral de figuras de revolución mediante métodos de integración numérica (Simpson, Trapecios)10101010.Modelado: Resolución de EDOs de segundo orden para la dinámica del centro de masa mediante Runge-Kutta 5-6 y métodos multipaso

6. Flujo en Medios Porosos (Ecuación de Richards)Modelado de la difusión no lineal de humedad en papel comercial Whatman.Implementación: Resolución de la Ecuación de Richards mediante Diferencias Finitas en 1D y 2D y validación con la transformación de Boltzmann.

# Perfil del Desarrollador:

Diego F. Danelone: Analista Universitario de Sistemas (UTN FRSF) y Abogado (UNL)

# Clonar el repositorio

git clone https://github.com/ddanelone/AN-TP-Backend-FastApi.git

# Instalar dependencias

pip install -r requirements.txt

# Iniciar el servidor FastAPI

uvicorn main:app --reload

Accede a la documentación interactiva en http://localhost:8000/docs.
