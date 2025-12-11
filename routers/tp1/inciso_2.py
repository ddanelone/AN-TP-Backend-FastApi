from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from services.tp1.inciso_2 import CONSIGNA2, EXPLICACION_INCISO_2, PROBLEMAS_INCISO_2

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
    summary="Consigna  resolver",
    response_class=PlainTextResponse
)
def obtener_consigna():
    return CONSIGNA2
