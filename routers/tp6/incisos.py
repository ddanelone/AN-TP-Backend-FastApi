from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, StreamingResponse
from services.tp6 import service_inciso_a, service_inciso_b, service_inciso_c, service_inciso_d, service_inciso_e, service_inciso_f

# CORRECCIÓN: Quitamos el prefix="/api/tp6" aquí. Main.py ya lo pone.
router = APIRouter(tags=["TP6"])

# --- INCISO A ---
@router.get("/inciso-a/consigna", response_class=PlainTextResponse)
def a_consigna(): return service_inciso_a.get_consigna()

@router.get("/inciso-a/explicacion", response_class=PlainTextResponse)
def a_explicacion(): return service_inciso_a.get_explicacion()

@router.get("/inciso-a/console-output", response_class=PlainTextResponse)
def a_console(): return service_inciso_a.get_console()

@router.get("/inciso-a/grafico", response_class=StreamingResponse)
def a_graph(): return StreamingResponse(service_inciso_a.get_grafico(), media_type="image/png")

# --- INCISO B ---
@router.get("/inciso-b/consigna", response_class=PlainTextResponse)
def b_consigna(): return service_inciso_b.get_consigna()

@router.get("/inciso-b/explicacion", response_class=PlainTextResponse)
def b_explicacion(): return service_inciso_b.get_explicacion()

@router.get("/inciso-b/console-output", response_class=PlainTextResponse)
def b_console(): return service_inciso_b.get_console()

@router.get("/inciso-b/grafico-perfiles", response_class=StreamingResponse)
def b_graph1(): return StreamingResponse(service_inciso_b.get_grafico_perfiles(), media_type="image/png")

@router.get("/inciso-b/grafico-boltzmann", response_class=StreamingResponse)
def b_graph2(): return StreamingResponse(service_inciso_b.get_grafico_frente(), media_type="image/png")

@router.get("/inciso-b/grafico-boltzmann-zoom", response_class=StreamingResponse)
def b_graph3(): return StreamingResponse(service_inciso_b.get_grafico_zoom(), media_type="image/png")

# --- INCISO C ---
@router.get("/inciso-c/consigna", response_class=PlainTextResponse)
def c_consigna(): return service_inciso_c.get_consigna()

@router.get("/inciso-c/explicacion", response_class=PlainTextResponse)
def c_explicacion(): return service_inciso_c.get_explicacion()

@router.get("/inciso-c/console-output", response_class=PlainTextResponse)
def c_console(): return service_inciso_c.get_console()

@router.get("/inciso-c/grafico-error", response_class=StreamingResponse)
def c_graph(): return StreamingResponse(service_inciso_c.get_grafico_error(), media_type="image/png")

# --- INCISO D ---
@router.get("/inciso-d/consigna", response_class=PlainTextResponse)
def d_consigna(): return service_inciso_d.get_consigna()

@router.get("/inciso-d/explicacion", response_class=PlainTextResponse)
def d_explicacion(): return service_inciso_d.get_explicacion()

@router.get("/inciso-d/console-output", response_class=PlainTextResponse)
def d_console(): return service_inciso_d.get_console()

@router.get("/inciso-d/grafico-1d", response_class=StreamingResponse)
def d_graph1(): return StreamingResponse(service_inciso_d.get_grafico_1d(), media_type="image/png")

@router.get("/inciso-d/grafico-2d", response_class=StreamingResponse)
def d_graph2(): return StreamingResponse(service_inciso_d.get_grafico_2d(), media_type="image/png")

# --- INCISO E ---
@router.get("/inciso-e/consigna", response_class=PlainTextResponse)
def e_consigna(): return service_inciso_e.get_consigna()

@router.get("/inciso-e/explicacion", response_class=PlainTextResponse)
def e_explicacion(): return service_inciso_e.get_explicacion()

@router.get("/inciso-e/console-output", response_class=PlainTextResponse)
def e_console(): return service_inciso_e.get_console()

@router.get("/inciso-e/grafico", response_class=StreamingResponse)
def e_graph(): return StreamingResponse(service_inciso_e.get_grafico(), media_type="image/png")

# --- INCISO F ---
@router.get("/inciso-f/consigna", response_class=PlainTextResponse)
def f_consigna(): return service_inciso_f.get_consigna()

@router.get("/inciso-f/explicacion", response_class=PlainTextResponse)
def f_explicacion(): return service_inciso_f.get_explicacion()

@router.get("/inciso-f/console-output", response_class=PlainTextResponse)
def f_console(): return service_inciso_f.get_console()

@router.get("/inciso-f/grafico-costos", response_class=StreamingResponse)
def f_graph(): return StreamingResponse(service_inciso_f.get_grafico_costos(), media_type="image/png")