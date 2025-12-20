# routers/tp5/inciso_2.py
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse
from services.tp5 import service_inciso_2

router = APIRouter(prefix="/inciso-2", tags=["TP5 - Inciso 2"])

@router.get("/consigna", response_class=PlainTextResponse)
def get_consigna():
    return service_inciso_2.CONSIGNA

@router.get("/problemas", response_class=PlainTextResponse)
def get_problemas():
    return service_inciso_2.PROBLEMAS

@router.get("/console-output", response_class=PlainTextResponse)
def get_console_output_data():
    """
    Devuelve los resultados numéricos formateados como tabla Markdown.
    """
    return service_inciso_2.get_console_output()

@router.get("/grafico-comparativa")
def get_grafico_comparativa():
    return StreamingResponse(
        service_inciso_2.generar_grafico_final(), 
        media_type="image/png"
    )

@router.get("/grafico-fase")
def get_grafico_fase():
    return StreamingResponse(
        service_inciso_2.generar_grafico_fase(), 
        media_type="image/png"
    )

@router.get("/grafico-error")
def get_grafico_error():
    return StreamingResponse(
        service_inciso_2.generar_grafico_error(), 
        media_type="image/png"
    )