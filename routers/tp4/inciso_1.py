from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse
from services.tp4 import service_inciso_1

router = APIRouter(
    prefix="/inciso-1",
    tags=["TP4 - Procesamiento de Imágenes (Inciso 1)"]
)

@router.get("/consigna", summary="Obtener consigna del punto 1", response_class=PlainTextResponse)
def get_consigna():
    return service_inciso_1.CONSIGNA

@router.get("/explicacion", summary="Explicación del método", response_class=PlainTextResponse)
def get_explicacion():
    return service_inciso_1.EXPLICACION

@router.get("/console-output", summary="Logs del procesamiento", response_class=PlainTextResponse)
def get_console_output():
    return service_inciso_1.obtener_logs()

@router.get("/grafico-procesamiento", summary="Imagen de ejemplo del procesamiento (1a)")
def get_grafico_procesamiento():
    imagen = service_inciso_1.generar_grafico_procesamiento()
    return StreamingResponse(imagen, media_type="image/png")

@router.get("/grafico-trayectoria", summary="Gráfico vertical CM vs tiempo (1b)")
def get_grafico_trayectoria():
    imagen = service_inciso_1.generar_grafico_trayectoria_vertical()
    return StreamingResponse(imagen, media_type="image/png")

@router.get("/grafico-horizontal", summary="Gráfico horizontal CM vs tiempo (1b)")
def get_grafico_horizontal():
    imagen = service_inciso_1.generar_grafico_posicion_horizontal()
    return StreamingResponse(imagen, media_type="image/png")

@router.get("/console-output2", summary="Salida formateada consola", response_class=PlainTextResponse)
def get_console_output2():
    return service_inciso_1.obtener_salida_consola()