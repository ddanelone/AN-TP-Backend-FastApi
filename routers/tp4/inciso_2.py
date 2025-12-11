from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse
from services.tp4 import service_inciso_2

router = APIRouter(
    prefix="/inciso-2",
    tags=["TP4 - Ángulos de Contacto (Inciso 2)"]
)

@router.get("/consigna", summary="Consigna Punto 2", response_class=PlainTextResponse)
def get_consigna():
    return service_inciso_2.CONSIGNA

@router.get("/explicacion", summary="Análisis 2a y 2c (Métodos y Dinámica)", response_class=PlainTextResponse)
def get_explicacion():
    return service_inciso_2.EXPLICACION

@router.get("/datos-json", summary="Datos crudos de ángulos (para inspección)")
def get_datos():
    return JSONResponse(content=service_inciso_2.obtener_datos_angulos())

@router.get("/grafico-angulos", summary="Gráfico Ángulos vs Tiempo (2b)")
def get_grafico():
    imagen = service_inciso_2.generar_grafico_angulos()
    if imagen:
        return StreamingResponse(imagen, media_type="image/png")
    return PlainTextResponse("No hay datos de contacto para graficar.")
 
@router.get("/console-output", summary="Salida formateada consola (Promedios)", response_class=PlainTextResponse)
def get_console_output():
    return service_inciso_2.obtener_salida_consola()

@router.get("/grafico-ajuste-detalle", summary="Detalle Ajuste Frame 28 (2a)",
            description="Muestra los puntos del contorno y las curvas ajustadas (Spline vs Poly) para el Frame 28.")
def get_grafico_detalle():
    imagen = service_inciso_2.generar_grafico_ajuste_frame28()
    if imagen:
        return StreamingResponse(imagen, media_type="image/png")
    return PlainTextResponse("No se pudo generar el detalle del ajuste (Frame 28).")