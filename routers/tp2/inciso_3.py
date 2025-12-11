from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse, FileResponse
from services.tp2 import inciso_3

router = APIRouter(prefix="/inciso_3", tags=["TP2 - Esteganografía con la Transformada 2D de Fourier - Inciso 3"])

@router.post("/ocultar", response_class=PlainTextResponse, summary="Ocultar imagen usando TF2D y paridad")
def ocultar_imagen(delta: int = Body(..., description="Valor de delta a utilizar")):
    """
    Oculta una imagen dentro de otra modificando la TF2D con un valor arbitrario `delta`
    y codificación de bits mediante la paridad de `q`. Se guarda la imagen estego.
    """
    return inciso_3.ocultar_imagen_post(delta)

@router.post("/extraer", response_class=PlainTextResponse, summary="Extraer imagen oculta")
def extraer_imagen(delta: int = Body(..., description="Valor de delta usado al ocultar")):
    """
    Extrae la imagen oculta desde la imagen estego generada con TF2D y paridad,
    utilizando el mismo valor de `delta` con el que fue ocultada.
    """
    return inciso_3.extraer_imagen_post(delta)

@router.get("/portadora", summary="Mostrar imagen portadora")
def get_portadora():
    return FileResponse(inciso_3.get_portadora_path(), media_type="image/png")

@router.get("/oculta", summary="Mostrar imagen oculta original")
def get_oculta():
    return FileResponse(inciso_3.get_oculta_path(), media_type="image/png")

@router.get("/estego", summary="Mostrar imagen estego generada")
def get_estego():
    return inciso_3.get_estego_as_png()

@router.get("/recuperada", summary="Mostrar imagen recuperada")
def get_recuperada():
    return FileResponse(inciso_3.get_recuperada_path(), media_type="image/png")

@router.get("/consigna", response_class=PlainTextResponse, summary="Mostrar consigna del ejercicio")
def get_consigna():
    return inciso_3.CONSIGNA_DELTA

@router.get("/explicacion", response_class=PlainTextResponse, summary="Explicación teórica del método")
def get_explicacion():
    return inciso_3.EXPLICACION_DELTA

@router.get("/problemas", response_class=PlainTextResponse, summary="Problemas y dificultades encontradas")
def get_problemas():
    return inciso_3.PROBLEMAS_DELTA

@router.get("/conclusiones", response_class=PlainTextResponse, summary="Conclusiones del análisis")
def get_conclusiones():
    return inciso_3.CONCLUSIONES_DELTA
 
