from PIL import Image
import numpy as np
import os

# === Paths ===
BASE_PATH = "data/tp2/"
IMG_PORTADORA = os.path.join(BASE_PATH, "globo.png")
IMG_OCULTA = os.path.join(BASE_PATH, "wp.png")
IMG_ESTEGANOGRAFICA = os.path.join(BASE_PATH, "imagen_estego2.tiff")
IMG_RECUPERADA = os.path.join(BASE_PATH, "imagen_recuperada.png")

# === Variables globales (persistentes en el backend) ===
_ultima_posiciones = None  # Para guardar las posiciones usadas en el encoding
_repeticiones = 7  # Nivel de redundancia

# === Funciones utilitarias ===
def cargar_grises(path):
    return np.array(Image.open(path).convert('L'))

def obtener_posiciones_validas(shape, radio_exclusion=40, n=0):
    h, w = shape
    centro = (h // 2, w // 2)
    Y, X = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
    dist = np.sqrt((Y - centro[0]) ** 2 + (X - centro[1]) ** 2)
    mask = dist > radio_exclusion
    indices = np.argwhere(mask)
    posiciones = []
    usados = set()
    for i, j in indices:
        ci, cj = (-i) % h, (-j) % w
        if (ci, cj) not in usados and (i, j) not in usados and (i, j) < (ci, cj):
            posiciones.append((i, j, ci, cj))
            usados.add((i, j))
            usados.add((ci, cj))
    np.random.shuffle(posiciones)
    return posiciones[:n]

# === Codificador ===
def ocultar_imagen_en_fft():
    global _ultima_posiciones

    portadora = cargar_grises(IMG_PORTADORA)
    oculta = cargar_grises(IMG_OCULTA)
    bits = np.unpackbits(oculta.flatten())
    bits_rep = np.repeat(bits, _repeticiones)

    posiciones = obtener_posiciones_validas(portadora.shape, radio_exclusion=40, n=len(bits_rep))
    _ultima_posiciones = posiciones  # Guardamos para el decoder

    portadora_f = np.fft.fft2(portadora)

    for idx, bit in enumerate(bits_rep):
        i, j, ci, cj = posiciones[idx]
        val = portadora_f[i, j]
        imag = abs(val.imag) if bit == 1 else -abs(val.imag)
        portadora_f[i, j] = complex(val.real, imag)
        portadora_f[ci, cj] = complex(val.real, -imag)

    estego = np.real(np.fft.ifft2(portadora_f))
    estego = np.clip(estego, 0, 255).astype(np.uint8)
    Image.fromarray(estego).save(IMG_ESTEGANOGRAFICA, format='TIFF')

    return f"Imagen '{IMG_OCULTA}' ocultada correctamente en '{IMG_ESTEGANOGRAFICA}'. Total bits (c/ redundancia): {len(bits_rep)}"

# === Decodificador ===
def extraer_imagen_de_fft():
    global _ultima_posiciones

    if _ultima_posiciones is None:
        return "Primero debe ejecutarse el ocultamiento para obtener las posiciones"

    estego = cargar_grises(IMG_ESTEGANOGRAFICA)
    oculta_original = cargar_grises(IMG_OCULTA)
    shape_oculta = oculta_original.shape

    estego_f = np.fft.fft2(estego)
    bits_extraidos = []

    for i, j, _, _ in _ultima_posiciones:
        val = estego_f[i, j]
        bit = 1 if val.imag >= 0 else 0
        bits_extraidos.append(bit)

    bits = []
    for i in range(0, len(bits_extraidos), _repeticiones):
        votos = bits_extraidos[i:i+_repeticiones]
        bits.append(int(np.sum(votos) >= (_repeticiones / 2)))

    bits_array = np.array(bits[:shape_oculta[0] * shape_oculta[1] * 8], dtype=np.uint8)
    pixels = np.packbits(bits_array).reshape(shape_oculta)
    Image.fromarray(pixels).save(IMG_RECUPERADA)

    # Métricas
    iguales = np.sum(pixels == oculta_original)
    total = oculta_original.size
    porcentaje_igual = 100 * iguales / total
    ecm = np.mean((oculta_original.astype(np.int32) - pixels.astype(np.int32))**2)

    return (
        f"Imagen recuperada correctamente como '{IMG_RECUPERADA}'\n"
        f"Coincidencia total de píxeles: {iguales}/{total} ({porcentaje_igual:.2f}%)\n"
        f"Error cuadrático medio (ECM): {ecm:.2f}"
    )

# === Funciones de visualización (devuelven rutas) ===
def get_portadora_path():
    return IMG_PORTADORA

def get_oculta_path():
    return IMG_OCULTA

def get_estego_path():
    return IMG_ESTEGANOGRAFICA

def get_recuperada_path():
    return IMG_RECUPERADA

# === Texto enriquecido para endpoints informativos ===

CONSIGNA_FFT = """
Consigna del inciso 2: Esteganografía por Transformada de Fourier 2D

Se solicita ocultar una imagen monocromática dentro de otra utilizando la Transformada de Fourier 2D.
Se debe aplicar una codificación sobre los coeficientes de la imagen portadora para introducir, con redundancia, los bits de la imagen a ocultar. Luego, debe implementarse el decodificador correspondiente para verificar la calidad de recuperación de la imagen oculta.

Ambas imágenes son en escala de grises, donde cada píxel representa un byte de información.
"""

EXPLICACION_FFT = """
🧠 Explicación teórica del método FFT para esteganografía

Se utiliza la FFT 2D para pasar la imagen portadora al dominio de la frecuencia.
Luego se seleccionan pares de coeficientes simétricos y se codifica el bit modificando el signo de la parte imaginaria:
- Bit 1 → parte imaginaria positiva
- Bit 0 → parte imaginaria negativa

Se aplica redundancia (repeticiones) y se preserva la simetría conjugada para mantener una imagen real al aplicar la inversa. La imagen modificada se guarda como TIFF.

Para decodificar, se invierte el proceso y se reconstruyen los bytes originales.
"""

PROBLEMAS_FFT = """
⚠️ Problemas encontrados

- Mantener la simetría conjugada para no alterar la realcez de la imagen
- Selección de posiciones válidas alejadas del centro para evitar artefactos
- Necesidad de repetir los bits para mejorar la robustez (votación)
- Gestión de las posiciones usadas: en esta implementación se mantienen en memoria (no se serializan)
"""

CONCLUSIONES_FFT = """
📌 Conclusiones

- El método FFT permite ocultar imágenes completas sin afectar visiblemente la imagen portadora
- El nivel de recuperación depende fuertemente del número de repeticiones y el tamaño de las imágenes
- La votación por mayoría mejora la robustez sin aumentar el tamaño del archivo
- El uso de imágenes reales y archivos TIFF permite resultados más fieles
"""
