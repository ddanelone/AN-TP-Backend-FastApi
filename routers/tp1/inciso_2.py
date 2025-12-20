
# routers/tp1/inciso_2.py
# routers/tp1/inciso_2.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, Response
from services.tp1.inciso_2 import (
    CONSIGNA2, 
    EXPLICACION_INCISO_2, 
    PROBLEMAS_INCISO_2,
    generar_grafico_zoom_img
)

router = APIRouter(
    prefix="/inciso-2",
    tags=["TP1 - Transformada de Fourier (Inciso 2)"]
)

@router.get(
    "/explicacion",
    summary="Explicación teórica sobre la Transformada de Fourier aplicada al EEG",
    description="Analiza qué aporta la FFT en señales cerebrales y cómo se diferencian las señales según la etapa epiléptica.",
    response_class=PlainTextResponse
)
def obtener_explicacion_inciso_2():
    return EXPLICACION_INCISO_2

@router.get(
    "/problemas",
    summary="Resolución y análisis del inciso 2 del TP1",
    description="Describe los pasos realizados, observaciones, dificultades y conclusiones obtenidas al aplicar la FFT.",
    response_class=PlainTextResponse
)
def obtener_problemas_inciso_2():
    return PROBLEMAS_INCISO_2

@router.get(
    "/consigna",
    summary="Consigna a resolver",
    response_class=PlainTextResponse
)
def obtener_consigna():
    return CONSIGNA2

@router.get(
    "/grafico-zoom",
    summary="Gráfico de detalle (Zoom 1s)",
    description="Devuelve una imagen PNG comparando la señal original vs filtrada en el primer segundo de registro.",
    responses={
        200: {"content": {"image/png": {}}},
        500: {"description": "Error al generar el gráfico o archivos no encontrados"}
    },
    response_class=Response
)
def obtener_grafico_zoom():
    img_buf = generar_grafico_zoom_img()
    if img_buf is None:
        raise HTTPException(status_code=500, detail="No se pudieron cargar los archivos de señales (Signal_x.txt). Verifique la ruta DATA_PATH en el servicio.")
    
    return Response(content=img_buf.getvalue(), media_type="image/png")