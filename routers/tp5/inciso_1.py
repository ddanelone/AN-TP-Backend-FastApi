from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse
from services.tp5 import service_inciso_1

router = APIRouter(prefix="/inciso-1", tags=["TP5 - Inciso 1"])

@router.get("/consigna", response_class=PlainTextResponse)
def c(): return service_inciso_1.CONSIGNA

@router.get("/problemas", response_class=PlainTextResponse)
def p(): return service_inciso_1.PROBLEMAS

@router.get("/console-output", response_class=PlainTextResponse)
def o(): return service_inciso_1.get_console_output()

@router.get("/grafico-volumen")
def g(): return StreamingResponse(service_inciso_1.generar_grafico_volumen(), media_type="image/png")

@router.get("/grafico-radio")
def g_rad(): return StreamingResponse(service_inciso_1.generar_grafico_radio(), media_type="image/png")

@router.get("/grafico-perfil-80", summary="Perfil Ajustado Frame 80")
def get_grafico_perfil():
    imagen = service_inciso_1.generar_grafico_perfil_80()
    if imagen:
        return StreamingResponse(imagen, media_type="image/png")
    return PlainTextResponse("No se pudo procesar el Frame 80.")