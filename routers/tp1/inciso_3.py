from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse
from services.tp1.inciso_3 import (
    CONSIGNA3,
    generar_grafico_potencia_barras,
    generar_grafico_potencia_lineas,
    EXPLICACION_INCISO_3,
    PROBLEMAS_INCISO_3
)

router = APIRouter(
    prefix="/inciso-3",
    tags=["TP1 - Potencia Espectral (Inciso 3)"]
)

@router.get(
    "/consigna",
    summary="Consigna  resolver",
    response_class=PlainTextResponse
)
def obtener_consigna():
    return CONSIGNA3


@router.get("/explicacion", summary="Explicación teórica del análisis de potencia espectral", response_class=PlainTextResponse)
def obtener_explicacion():
    return EXPLICACION_INCISO_3

@router.get("/problemas", summary="Resolución, problemas y conclusiones del inciso 3", response_class=PlainTextResponse)
def obtener_problemas():
    return PROBLEMAS_INCISO_3

@router.get("/grafico1", summary="Potencia espectral por banda (barras)")
def grafico_barras():
    return StreamingResponse(generar_grafico_potencia_barras(), media_type="image/png")

@router.get("/grafico2", summary="Potencia espectral por banda (líneas)")
def grafico_lineas():
    return StreamingResponse(generar_grafico_potencia_lineas(), media_type="image/png")
