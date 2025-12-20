# routers/tp2/inciso_1.py
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from services.tp2 import inciso_1

router = APIRouter(prefix="/inciso_1", tags=["TP2 - Esteganografía LSB - Inciso 1"])

@router.post("/ocultar", response_class=PlainTextResponse, summary="Ocultar mensaje en imagen")
def ocultar_mensaje(mensaje: str = Query(..., description="Mensaje de texto a ocultar")):
    """
    Oculta un mensaje de texto en una imagen utilizando el método LSB.
    Guarda la imagen esteganográfica en disco.

    - **mensaje**: Texto plano a ocultar (se agrega '&' al final automáticamente)
    """
    return inciso_1.ocultar_mensaje_en_imagen(mensaje)

@router.get("/extraer", response_class=PlainTextResponse, summary="Extraer mensaje oculto")
def extraer_mensaje():
    """
    Extrae el mensaje oculto desde la imagen generada con el método LSB.
    """
    return inciso_1.extraer_mensaje_de_imagen()

@router.get("/consigna", response_class=PlainTextResponse, summary="Consigna original")
def get_consigna():
    """
    Devuelve la consigna del inciso 1 formateada en LaTeX.
    """
    return inciso_1.CONSIGNA_LSB

@router.get("/conclusiones", response_class=PlainTextResponse, summary="Explicación técnica y conclusiones")
def get_conclusiones():
    """
    Devuelve la explicación técnica del método LSB, fórmulas de capacidad y conclusiones en formato LaTeX.
    """
    return inciso_1.obtener_conclusiones()

@router.get("/imagen-original")
def get_imagen_original():
    try:
        return inciso_1.obtener_imagen_portadora()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/imagen-estego")
def get_imagen_estego():
    try:
        return inciso_1.obtener_imagen_estego()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))