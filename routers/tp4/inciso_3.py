from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse
from services.tp4 import service_inciso_3

router = APIRouter(
    prefix="/inciso-3",
    tags=["TP4 - Variables Auxiliares (Inciso 3)"]
)

@router.get("/consigna", response_class=PlainTextResponse)
def get_consigna():
    return service_inciso_3.CONSIGNA

@router.get("/explicacion", response_class=PlainTextResponse)
def get_explicacion():
    return service_inciso_3.EXPLICACION

@router.get("/grafico-sf", summary="Factor de Esparcimiento")
def get_grafico_sf():
    return StreamingResponse(service_inciso_3.generar_grafico_sf(), media_type="image/png")

@router.get("/grafico-simetria", summary="Simetría Izq/Der")
def get_grafico_simetria():
    return StreamingResponse(service_inciso_3.generar_grafico_simetria(), media_type="image/png")

@router.get("/grafico-energia", summary="Energía Cinética")
def get_grafico_energia():
    return StreamingResponse(service_inciso_3.generar_grafico_energia(), media_type="image/png")
 
@router.get("/console-output", summary="Salida formateada consola (Estadísticas)", response_class=PlainTextResponse)
def get_console_output():
    return service_inciso_3.obtener_salida_consola()