import io
from PIL import Image
import numpy as np
import os
from fastapi.responses import StreamingResponse


# Paths fijos (pueden generalizarse después)
IMAGEN_ORIGINAL_PATH = "data/tp2/imagen_portadora.png"
IMAGEN_ESTEGANOGRAFICA_PATH = "data/tp2/imagen_estego.png"


def mensaje_a_binario(mensaje: str) -> str:
    mensaje += "&"  # Marcador de fin
    return ''.join([format(ord(c), '08b') for c in mensaje])


def binario_a_mensaje(binario: str) -> str:
    chars = [binario[i:i+8] for i in range(0, len(binario), 8)]
    mensaje = ''.join([chr(int(b, 2)) for b in chars])
    return mensaje.split("&")[0]  # Cortar al marcador


def ocultar_mensaje_en_imagen(mensaje: str) -> str:
    try:
        imagen = Image.open(IMAGEN_ORIGINAL_PATH).convert('L')
        datos = np.array(imagen).flatten()
        bin_mensaje = mensaje_a_binario(mensaje)

        if len(bin_mensaje) > len(datos):
            max_chars = len(datos) // 8
            raise ValueError(f"Mensaje demasiado largo. Máximo permitido: {max_chars} caracteres.")

        for i, bit in enumerate(bin_mensaje):
            datos[i] = (datos[i] & 0b11111110) | int(bit)

        nueva_imagen = Image.fromarray(np.reshape(datos, imagen.size[::-1]).astype(np.uint8))
        nueva_imagen.save(IMAGEN_ESTEGANOGRAFICA_PATH)

        return f"✅ Imagen guardada correctamente en {IMAGEN_ESTEGANOGRAFICA_PATH}"

    except Exception as e:
        return f"❌ Error al ocultar mensaje: {str(e)}"


def extraer_mensaje_de_imagen() -> str:
    try:
        imagen = Image.open(IMAGEN_ESTEGANOGRAFICA_PATH).convert('L')
        datos = np.array(imagen).flatten()

        bits = [str(pixel & 1) for pixel in datos]
        binario = ''.join(bits)

        mensaje = binario_a_mensaje(binario)

        return f"🕵️ Mensaje extraído correctamente: '{mensaje}'"

    except Exception as e:
        return f"❌ Error al extraer mensaje: {str(e)}"

def obtener_imagen_portadora() -> StreamingResponse:
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
 
CONSIGNA_LSB = """
1. Modificar el último bit significativo de cada píxel en una imagen original para ocultar un mensaje. Para ello,
se deben seguir los siguientes pasos: Primero, utilizar una imagen en formato .png o .jpg. A continuación,
el mensaje que se desea ocultar debe ser convertido a texto ASCII utilizando un programa o script que
realice la conversión. Por ejemplo, el mensaje ”Hola” se convierte en los valores ASCII correspondientes:
[72, 111, 108, 97]. Agregar el símbolo ”&” al final del mensaje para marcar el final del mismo. Luego, este
texto ASCII debe ser transformado a binario, de manera que cada valor ASCII se representa en formato
binario de 8 bits. Por ejemplo, el número 72 (código ASCII de ’H’) se convierte en 01001000 en binario.
Una vez que el mensaje ha sido convertido a binario, se debe modificar la imagen. Para cada píxel de la
imagen, se debe reemplazar el último bit significativo por el bit del mensaje en binario. Si el valor del píxel
es, por ejemplo, 11001011, se cambiará el último bit de acuerdo al bit del mensaje que se está codificando
(si es 1 o 0). Después de modificar todos los píxeles de la imagen con los bits del mensaje, se debe guardar
la imagen modificada en un nuevo archivo como imagen estego. El siguiente paso es crear un decodificador
que pueda extraer el mensaje oculto. Este decodificador deberá leer los bits modificados de los últimos
bits significativos de cada píxel, reconstruir el mensaje en binario y convertirlo nuevamente a texto ASCII.
Finalmente, se debe verificar que el mensaje decodificado coincida con el mensaje original. Mostrar tanto
la imagen original como la imagen estego, y comparar el mensaje decodificado con el mensaje original.
Obtener conclusiones a partir de la comparacion entre ambas imagenes. ¿Cual es la longitud maxima de
un mensaje que se puede transmitir de acuerdo al tamañ         o de la imagen original? ¿Como podria ampliar
la cantidad de informacion enviada utilizando la misma imagen?
"""