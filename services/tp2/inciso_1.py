# services/tp2/inciso_1.py
import io
import os
import numpy as np
from PIL import Image
from fastapi.responses import StreamingResponse

# --- Configuración y Constantes ---

# Paths fijos
IMAGEN_ORIGINAL_PATH = "data/tp2/imagen_portadora.png"
IMAGEN_ESTEGANOGRAFICA_PATH = "data/tp2/imagen_estego.png"

CONSIGNA_LSB = r"""
1. **Esteganografía LSB (Least Significant Bit)**

Modificar el último bit significativo de cada píxel en una imagen original para ocultar un mensaje.

**Pasos a seguir:**

1.  **Conversión del mensaje**: Convertir el texto a ocultar a su representación ASCII y luego a binario (8 bits por caracter).
    * Ejemplo: "Hola" $\rightarrow [72, 111, 108, 97]$.
    * Binario ($H=72$): $01001000_2$.
    * *Nota*: Agregar un carácter delimitador (ej. `&`) al final para saber cuándo detener la lectura.

2.  **Modificación de la imagen**: Para cada píxel de la imagen (flattened), reemplazar el bit menos significativo (LSB) con un bit del mensaje.
    * Operación lógica: Sea $P$ el valor del píxel y $b$ el bit del mensaje:
        $$ P_{nuevo} = (P \land 11111110_2) \lor b $$
    * Ejemplo: Si $P = 11001011_2$ y el bit del mensaje es $0$, el nuevo píxel será $11001010_2$.

3.  **Extracción**: Crear un decodificador que lea los LSB de cada píxel, reconstruya los bytes y los convierta nuevamente a caracteres ASCII hasta encontrar el delimitador.

**Preguntas de análisis:**
* ¿Cuál es la longitud máxima de un mensaje que se puede transmitir de acuerdo al tamaño de la imagen original?
* ¿Cómo podría ampliar la cantidad de información enviada utilizando la misma imagen?
"""

CONCLUSIONES_LSB = r"""
### 🔬 Análisis y Conclusiones: Método LSB

**1. Fundamento Teórico**
El método LSB (*Least Significant Bit*) aprovecha la limitación del sistema visual humano. En una imagen de 8 bits (escala de grises), cada píxel tiene un valor entre $0$ y $255$. Modificar el último bit implica alterar el valor de intensidad en $\pm 1$.
$$ \Delta I = |P_{original} - P_{estego}| \le 1 $$
Esta variación es **imperceptible** a simple vista, manteniendo la imagen esteganográfica ("estego") visualmente idéntica a la portadora.

**2. Capacidad de Almacenamiento**
La capacidad máxima ($C_{max}$) está determinada directamente por la cantidad de píxeles de la imagen. Dado que escondemos **1 bit por píxel**:

$$ C_{max} \text{ (bytes)} = \frac{Ancho \times Alto}{8} $$

* Si la imagen es de $512 \times 512$ píxeles:
    $$ C_{max} = \frac{262,144}{8} = 32,768 \text{ bytes} \approx 32 \text{ KB} $$

**3. Ampliación de Información**
Para enviar más datos usando la misma imagen, se pueden utilizar los **k bits menos significativos** (ej. los últimos 2 o 3 bits).
* **Nueva Capacidad**: $C'_{max} = k \times \frac{W \times H}{8}$.
* **Compromiso (Trade-off)**: Al aumentar $k$, la distorsión aumenta exponencialmente. Modificar el bit 2 implica cambios de $\pm 2$, el bit 3 de $\pm 4$, etc. Esto incrementa el *Error Cuadrático Medio* (MSE) y hace que el ruido sea visible, delatando la existencia del mensaje.
"""

# --- Funciones Lógicas ---

def mensaje_a_binario(mensaje: str) -> str:
    mensaje += "&"  # Marcador de fin
    return ''.join([format(ord(c), '08b') for c in mensaje])

def binario_a_mensaje(binario: str) -> str:
    # Agrupamos de a 8 bits
    chars = [binario[i:i+8] for i in range(0, len(binario), 8)]
    # Convertimos a int y luego a char
    texto_completo = "".join([chr(int(b, 2)) for b in chars if len(b) == 8])
    return texto_completo.split("&")[0]  # Cortar al marcador

def ocultar_mensaje_en_imagen(mensaje: str) -> str:
    try:
        if not os.path.exists(IMAGEN_ORIGINAL_PATH):
            return "Error: No se encontró la imagen portadora en el servidor."

        imagen = Image.open(IMAGEN_ORIGINAL_PATH).convert('L')
        datos = np.array(imagen).flatten()
        bin_mensaje = mensaje_a_binario(mensaje)

        if len(bin_mensaje) > len(datos):
            max_chars = len(datos) // 8
            raise ValueError(f"Mensaje demasiado largo. Máximo permitido: {max_chars} caracteres.")

        # Vectorización (más rápido que el loop for si fuera posible, pero mantenemos tu lógica por claridad o si prefieres loop)
        # Para mantener tu lógica exacta del loop:
        for i, bit in enumerate(bin_mensaje):
            # Limpiar LSB y poner el bit del mensaje
            datos[i] = (datos[i] & 0b11111110) | int(bit)

        nueva_imagen = Image.fromarray(np.reshape(datos, imagen.size[::-1]).astype(np.uint8))
        nueva_imagen.save(IMAGEN_ESTEGANOGRAFICA_PATH)

        return f"Imagen guardada correctamente en {IMAGEN_ESTEGANOGRAFICA_PATH}"

    except Exception as e:
        return f"Error al ocultar mensaje: {str(e)}"

def extraer_mensaje_de_imagen() -> str:
    try:
        if not os.path.exists(IMAGEN_ESTEGANOGRAFICA_PATH):
            return "Primero debes ocultar un mensaje para generar la imagen estego."

        imagen = Image.open(IMAGEN_ESTEGANOGRAFICA_PATH).convert('L')
        datos = np.array(imagen).flatten()

        # Extraer LSBs
        bits = [str(pixel & 1) for pixel in datos]
        binario = ''.join(bits)

        mensaje = binario_a_mensaje(binario)

        return f"Mensaje extraído correctamente: '{mensaje}'"

    except Exception as e:
        return f"Error al extraer mensaje: {str(e)}"

def obtener_imagen_portadora() -> StreamingResponse:
    if not os.path.exists(IMAGEN_ORIGINAL_PATH):
        raise FileNotFoundError("Imagen original no encontrada.")
        
    imagen = Image.open(IMAGEN_ORIGINAL_PATH).convert("L")
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": 'inline; filename="imagen_portadora.png"',
            "Content-Type": "image/png",
            "Cache-Control": "no-store"
        }
    )

def obtener_imagen_estego() -> StreamingResponse:
    if not os.path.exists(IMAGEN_ESTEGANOGRAFICA_PATH):
        raise FileNotFoundError("La imagen estego no fue generada todavía.")

    imagen = Image.open(IMAGEN_ESTEGANOGRAFICA_PATH).convert("L")
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": 'inline; filename="imagen_estego.png"',
            "Content-Type": "image/png",
            "Cache-Control": "no-store"
        }
    )

def obtener_conclusiones() -> str:
    return CONCLUSIONES_LSB