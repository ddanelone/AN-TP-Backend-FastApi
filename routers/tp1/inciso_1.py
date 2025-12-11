# /roers.tp1/inciso_1.py

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse
from services.tp1.inciso_1 import CONSIGNA, EXPLICACION_FRECUENCIAS, PROBLEMAS_INCISO_1, generar_grafico_comparativo
from services.tp1.inciso_1 import generar_grafico_fft_lineas, generar_grafico_fft_tallo

router = APIRouter(
    prefix="/inciso-1",
    tags=["TP1 - Análisis de señales EEG (Inciso 1)"]
)

@router.get(
    "/consigna",
    summary="Consigna  resolver",
    response_class=PlainTextResponse
)
def obtener_consigna():
    return CONSIGNA


@router.get("/grafico", summary="Comparación de señales EEG crudas y filtradas")
def obtener_grafico():
    imagen = generar_grafico_comparativo()
    return StreamingResponse(imagen, media_type="image/png")

@router.get("/grafico2", summary="Espectro FFT de señales EEG (línea continua)")
def obtener_grafico_fft():
    imagen = generar_grafico_fft_lineas()
    return StreamingResponse(imagen, media_type="image/png")

@router.get("/grafico3", summary="Espectro FFT de señales EEG (diagrama de tallo)")
def obtener_grafico_fft_tallo():
    imagen = generar_grafico_fft_tallo()
    return StreamingResponse(imagen, media_type="image/png")

@router.get(
    "/explicacion",
    summary="Explicación teórica de bandas de frecuencia en EEG",
    description="Devuelve una descripción de las bandas cerebrales y cómo se relacionan con las etapas de la epilepsia.",
    response_class=PlainTextResponse
)
def obtener_explicacion():
    return EXPLICACION_FRECUENCIAS

@router.get(
    "/problemas",
    summary="Descripción del análisis realizado en el TP1 - Inciso 1",
    description="Explicación general de los gráficos generados y las decisiones tomadas durante el procesamiento de las señales EEG.",
    response_class=PlainTextResponse
)
def obtener_problemas():
    return PROBLEMAS_INCISO_1