from fastapi import APIRouter
from fastapi.responses import StreamingResponse, PlainTextResponse
from matplotlib.pylab import fftfreq
import numpy as np
from services.tp1.inciso_4 import (
    CONSIGNA4,
    generar_grafico_autocorrelacion,
    generar_grafico_potencias_por_banda,
    generar_resumen_analisis_bandas,
    cargar_senales_filtradas,
    obtener_fs,
    obtener_etapas,
    EXPLICACION_INCISO_4,
    PROBLEMAS_INCISO_4,
)

router = APIRouter(
    prefix="/inciso-4",
    tags=["TP1 - Autocorrelación (Inciso 4)"]
)
@router.get(
    "/consigna",
    summary="Consigna  resolver",
    response_class=PlainTextResponse
)
def obtener_consigna():
    return CONSIGNA4

@router.get("/explicacion", summary="Explicación teórica de autocorrelación en señales EEG")
def obtener_explicacion_inciso_4():
    return PlainTextResponse(EXPLICACION_INCISO_4)


@router.get("/problemas", summary="Problemas, observaciones y conclusiones del inciso 4")
def obtener_problemas_inciso_4():
    return PlainTextResponse(PROBLEMAS_INCISO_4)


@router.get("/grafico1", summary="Gráfico de autocorrelación para las tres señales EEG")
def obtener_grafico_autocorrelacion():
    imagen = generar_grafico_autocorrelacion()
    return StreamingResponse(imagen, media_type="image/png")


@router.get("/grafico2", summary="Distribución de potencia relativa por banda de frecuencia")
def obtener_grafico_potencia_por_bandas():
    senales = cargar_senales_filtradas()
    fs = obtener_fs()
    ETAPAS = obtener_etapas()  # este lo necesitás para los labels del gráfico

    # Calcular potencias: lista de tuplas (frecuencia, espectro)
    potencias = [(fftfreq(len(s), 1/fs), np.abs(np.fft.fft(s))**2) for s in senales]

    imagen = generar_grafico_potencias_por_banda(potencias, ETAPAS)
    return StreamingResponse(imagen, media_type="image/png")


@router.get("/analisis-bandas", summary="Salida tipo consola con resumen por bandas y señales")
def obtener_analisis_bandas():
    senales = cargar_senales_filtradas()
    fs = obtener_fs()
    ETAPAS = obtener_etapas()

    potencias = [(fftfreq(len(s), 1/fs), np.abs(np.fft.fft(s))**2) for s in senales]

    texto = generar_resumen_analisis_bandas(potencias, ETAPAS)
    return PlainTextResponse(texto)

