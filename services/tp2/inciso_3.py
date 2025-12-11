import numpy as np
from PIL import Image
import io
from fastapi.responses import StreamingResponse
import imageio.v3 as iio

# === CONSTANTES ===
PORTADORA_PATH = "data/tp2/globo.png"
OCULTA_PATH = "data/tp2/wp.png"
ESTEGO_PATH = "data/tp2/imagen_estego2.png"
RECUPERADA_PATH = "data/tp2/imagen_recuperada2.png"

REP_GLOBAL = 3
SHAPE_OCULTA = None

CONSIGNA_DELTA = """
Modificar las componentes de la TF2D utilizando un parámetro arbitrario δ y una modificación basada en q.
Para cada componente a + ib, se debe calcular el nuevo valor de a′ y b′ utilizando la fórmula:
    a′ = signo · q · δ
Donde signo=1 si a >=0 y signo=-1 si a < 0, y q = abs(round(a/δ)).
En la paridad de q se guarda el bit secreto: será par si el bit que toca ocultar es un 0 e impar si el bit que toca ocultar es un 1.
Aplicar la transformada inversa para reconstruir la imagen modificada. Evaluar el impacto del parámetro delta.
"""

EXPLICACION_DELTA = """
Se utiliza la TF2D para alterar la parte real e imaginaria de cada componente espectral de la imagen portadora.
El bit secreto se codifica manipulando la paridad del valor q=|a/δ| redondeado, ajustando el valor de cada componente
para que tenga la paridad deseada.
La redundancia mejora la robustez al ruido al repetir bits múltiples veces.
"""

PROBLEMAS_DELTA = """
- Si δ es muy grande, la imagen estego pierde fidelidad visual.
- Si δ es muy pequeño, los bits ocultos pueden perderse por ruido o redondeo numérico.
- Elegir una δ óptima requiere prueba y error.
"""

CONCLUSIONES_DELTA = """
- El método permite un buen compromiso entre imperceptibilidad y capacidad.
- El valor de δ afecta la calidad visual y la robustez del mensaje.
- Repetir bits aumenta la confiabilidad a costa de capacidad útil.
"""

# === FUNCIONES ===
def cargar_grises(path):
    return np.array(Image.open(path).convert("L"), dtype=np.float64)

def ocultar(portadora, oculta, delta, rep):
    tf = np.fft.fftshift(np.fft.fft2(portadora))
    real = np.real(tf).flatten()
    imag = np.imag(tf).flatten()

    bits = np.unpackbits(oculta.astype(np.uint8).flatten())
    bits_rep = np.repeat(bits, rep)
    capacidad = min(len(bits_rep), len(real) + len(imag))
    bits_rep = bits_rep[:capacidad]

    real_mod = real.copy()
    imag_mod = imag.copy()
    idx_real = idx_imag = 0

    for i, bit in enumerate(bits_rep):
        if i % 2 == 0:
            a = real_mod[idx_real]
            signo = 1 if a >= 0 else -1
            q = int(np.round(abs(a) / delta))
            if q % 2 != bit:
                q += 1 if q % 2 == 0 else -1
            real_mod[idx_real] = signo * q * delta
            idx_real += 1
        else:
            b = imag_mod[idx_imag]
            signo = 1 if b >= 0 else -1
            q = int(np.round(abs(b) / delta))
            if q % 2 != bit:
                q += 1 if q % 2 == 0 else -1
            imag_mod[idx_imag] = signo * q * delta
            idx_imag += 1

    tf_mod = (real_mod + 1j * imag_mod).reshape(portadora.shape)
    tf_mod = np.fft.ifftshift(tf_mod)
    estego = np.fft.ifft2(tf_mod)
    estego = np.real(estego)
    estego = np.clip(estego, 0, 255)

    # Guardamos en float32 para no perder precisión
    np.save(ESTEGO_PATH.replace(".png", ".npy"), estego.astype(np.float32))
    return estego.astype(np.float32)

def extraer(estego, delta, rep, shape_recuperada):
    tf = np.fft.fftshift(np.fft.fft2(estego))
    real = np.real(tf).flatten()
    imag = np.imag(tf).flatten()

    total_bits = shape_recuperada[0] * shape_recuperada[1] * 8
    total_bits_rep = total_bits * rep

    bits_extraidos = []
    idx_real = idx_imag = 0
    for i in range(total_bits_rep):
        if i % 2 == 0:
            a = real[idx_real]; idx_real += 1
        else:
            a = imag[idx_imag]; idx_imag += 1
        q = int(np.round(abs(a) / delta))
        bits_extraidos.append(q % 2)

    bits_finales = []
    for i in range(0, len(bits_extraidos), rep):
        bloque = bits_extraidos[i:i+rep]
        if len(bloque) < rep:
            break
        bit = int(np.sum(bloque) >= (rep // 2 + 1))
        bits_finales.append(bit)

    bits_finales = np.array(bits_finales[: (len(bits_finales) // 8) * 8])
    pixeles = np.packbits(bits_finales)
    return pixeles[:shape_recuperada[0]*shape_recuperada[1]].reshape(shape_recuperada)

def ocultar_imagen_post(delta: float):
    global SHAPE_OCULTA
    portadora = cargar_grises(PORTADORA_PATH)
    oculta = cargar_grises(OCULTA_PATH)
    SHAPE_OCULTA = oculta.shape
    _ = ocultar(portadora, oculta, delta, REP_GLOBAL)
    return f"✅ Imagen estego generada con δ={delta} y guardada en formato binario (.npy)"

def extraer_imagen_post(delta: float):
    oculta = cargar_grises(OCULTA_PATH)
    shape = oculta.shape
    estego = np.load(ESTEGO_PATH.replace(".png", ".npy")).astype(np.float64)
    recuperada = extraer(estego, delta, REP_GLOBAL, shape)
    Image.fromarray(recuperada).save(RECUPERADA_PATH)
    iguales = np.sum(oculta.astype(np.uint8) == recuperada)
    total = oculta.size
    porcentaje = 100 * iguales / total
    return f"🎯 Recuperada: {iguales}/{total} ({porcentaje:.2f}%) píxeles iguales"

def get_estego_as_png():
    estego = np.load(ESTEGO_PATH.replace(".png", ".npy")).astype(np.float32)
    estego_uint8 = np.clip(estego, 0, 255).astype(np.uint8)
    image = Image.fromarray(estego_uint8)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")

def get_recuperada_path():
    return RECUPERADA_PATH

def get_portadora_path():
    return PORTADORA_PATH

def get_oculta_path():
    return OCULTA_PATH

CONSIGNA_DELTA = """
🎯 Consigna del inciso 3: Esteganografía por Transformada de Fourier 2D

Se debe modificar las componentes de la Transformada de Fourier 2D (TF2D) utilizando un parámetro arbitrario delta y una modificación basada en un valor q. Para cada componente compleja a + ib, se calcularán los nuevos valores a' y b' con la siguiente fórmula:

a' = signo × q × delta

donde

signo = 1 si a es mayor o igual a 0, y signo = -1 si a es menor que 0,

q es el valor absoluto del redondeo de a dividido por delta.

El mismo procedimiento se aplica para modificar b'.

La paridad de q es la que almacena el bit secreto: será par si el bit a ocultar es 0, e impar si el bit a ocultar es 1. Para asegurar esto, se suma 1 a q cuando sea necesario.

Finalmente, se aplica la transformada inversa de Fourier para reconstruir la imagen modificada, llamada imagen esteganográfica.

Se recomienda usar diferentes valores de delta en distintos órdenes de magnitud y analizar cómo afectan la imagen esteganográfica, especialmente en términos de la Transformada de Fourier y sus propiedades. Esto permitirá obtener conclusiones sobre el impacto de delta en la calidad y características de la imagen oculta.
"""