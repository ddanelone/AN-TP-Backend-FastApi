from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse
from services.tp5 import service_inciso_2

router = APIRouter(prefix="/inciso-2", tags=["TP5 - Inciso 2"])

@router.get("/consigna", response_class=PlainTextResponse)
def c(): return service_inciso_2.CONSIGNA

@router.get("/problemas", response_class=PlainTextResponse)
def p(): return service_inciso_2.PROBLEMAS

@router.get("/console-output", response_class=PlainTextResponse)
def o(): return service_inciso_2.get_console_output()

@router.get("/grafico-comparativa")
def g(): return StreamingResponse(service_inciso_2.generar_grafico_final(), media_type="image/png")

@router.get("/grafico-fase")
def g_fase(): return StreamingResponse(service_inciso_2.generar_grafico_fase(), media_type="image/png")

@router.get("/grafico-error")
def g_error(): return StreamingResponse(service_inciso_2.generar_grafico_error(), media_type="image/png")