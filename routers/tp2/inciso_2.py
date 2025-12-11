from fastapi import APIRouter
from fastapi.responses import FileResponse, PlainTextResponse
from services.tp2 import inciso_2
from PIL import Image
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/inciso_2", tags=["TP2 - Esteganografía con la Transformada 2D de Fourier - Inciso 2"])


@router.post("/ocultar", response_class=PlainTextResponse, summary="Ocultar imagen con FFT")
def ocultar_imagen():
    """
    Codifica la imagen `wp.png` dentro de la imagen `globo.png` utilizando la Transformada de Fourier 2D (FFT).
    Devuelve un resumen del proceso y cantidad de bits ocultos.
    """
    return inciso_2.ocultar_imagen_en_fft()

@router.get("/extraer", response_class=PlainTextResponse, summary="Extraer imagen oculta")
def extraer_imagen():
    """
    Extrae la imagen oculta desde la imagen esteganográfica (`imagen_estego.tiff`), 
    y la guarda como `imagen_recuperada.png`. Devuelve métricas de comparación.
    """
    return inciso_2.extraer_imagen_de_fft()

@router.get("/portadora", response_class=FileResponse, summary="Obtener imagen portadora")
def get_portadora():
    """
    Devuelve la imagen portadora original (`globo.png`) en escala de grises.
    """
    return FileResponse(inciso_2.get_portadora_path(), media_type="image/png")

@router.get("/oculta", response_class=FileResponse, summary="Obtener imagen oculta original")
def get_oculta():
    """
    Devuelve la imagen oculta original (`wp.png`) en escala de grises.
    """
    return FileResponse(inciso_2.get_oculta_path(), media_type="image/png")

@router.get("/estego-png", response_class=StreamingResponse)
def get_estego_png():
    tiff_path = inciso_2.get_estego_path()
    image = Image.open(tiff_path).convert("L")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")


@router.get("/recuperada", response_class=FileResponse, summary="Obtener imagen recuperada")
def get_recuperada():
    """
    Devuelve la imagen recuperada tras decodificar la información oculta (`imagen_recuperada.png`).
    """
    return FileResponse(inciso_2.get_recuperada_path(), media_type="image/png")

@router.get("/estego", response_class=FileResponse, summary="Obtener imagen esteganográfica")
def get_estego():
    """
    Devuelve la imagen con la información oculta (`imagen_estego.tiff`).
    """
    return FileResponse(inciso_2.get_estego_path(), media_type="image/tiff")


@router.get("/consigna", response_class=PlainTextResponse, summary="Consigna original")
def get_consigna():
    """
    Devuelve la consigna teórica del inciso 2 (ocultamiento con FFT).
    """
    return inciso_2.CONSIGNA_FFT


@router.get("/explicacion", response_class=PlainTextResponse, summary="Explicación teórica")
def get_explicacion():
    """
    Devuelve una explicación del método de esteganografía en el dominio de la frecuencia usando FFT 2D.
    """
    return inciso_2.EXPLICACION_FFT


@router.get("/problemas", response_class=PlainTextResponse, summary="Problemas encontrados")
def get_problemas():
    """
    Enumera las dificultades encontradas durante la implementación del método.
    """
    return inciso_2.PROBLEMAS_FFT


@router.get("/conclusiones", response_class=PlainTextResponse, summary="Conclusiones del trabajo")
def get_conclusiones():
    """
    Expone los resultados y conclusiones obtenidos tras aplicar y analizar el método FFT.
    """
    return inciso_2.CONCLUSIONES_FFT
