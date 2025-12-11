from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse, StreamingResponse
from models.tp3.gases import ParametrosIniciales
from fastapi import Body

from services.tp3.gases import EXPLICACION_INCISO_A, PROBLEMAS_INCISO_A, PROBLEMAS_INCISO_B, calcular_volumenes_con_params, comparar_metodos_vdw, ejecutar_metodos_con_comparacion, encontrar_intervalo, generar_grafico_gases, generar_grafico_general, generar_grafico_volumenes_comparados, generar_grafico_zoom, generar_imagen_error_volumen, obtener_funciones_numericas, resolver_resultado_gas, seleccionar_raiz_valida
from services.tp3.presentacion_gases import generar_grafico_comparativo_gral, generar_grafico_comparativo_z, generar_grafico_f_vdw

router = APIRouter(
    prefix="/gases",
    tags=["TP3 - Aplicación a un sistema de Gases"],
    responses={404: {"description": "Endpoint no encontrado"}}
)

@router.get("/consigna-gral", response_class=PlainTextResponse)
def obtener_consigna_planteo():
    consigna = """
   Aplicación en sistemas de gases
Un equipo de científicos inaugura un laboratorio subterráneo de alta presión ubicado en Bariloche. Su misión
es investigar el comportamiento de gases reales bajo condiciones extremas de presión y temperatura, como
las que se dan en el interior de planetas o en procesos industriales avanzados. Una de las primeras tareas del
equipo consiste en estudiar el comportamiento del dióxido de carbono (CO2), que sería utilizado como fluido
supercrítico en procesos de extracción. Los ingenieros logran mantener el gas a una temperatura constante de
200 K, y mediante un sistema de compresión controlada, lo someten a una presión de 5 MPa. Sin embargo,
al intentar calcular el volumen molar del gas usando la ley de los gases ideales:
                                       Pv = RT (1)
obtienen un resultado que no concuerda con las mediciones experimentales. Sospechan que a esa presión, las
interacciones moleculares y el volumen finito de las moléculas empiezan a jugar un papel importante, por lo
que deciden usar una versión mejorada: la ecuación de Van der Waals, que introduce correcciones al modelo
ideal.
"""
    return consigna.strip()
 
@router.get("/consigna-a", response_class=PlainTextResponse)
def obtener_consigna():
    consigna = """
2. a) Investigar cuales son las correcciones que introduce el modelo de Van der Waals. Determinar el volumen
real que tendría el gas bajo esas condiciones.
"""
    return consigna.strip()
 
@router.get("/consigna-b", response_class=PlainTextResponse)
def obtener_consignabis():
    consigna = """
2. b) Determinar nuevamente el volumen real del gas utilizando ahora una presion de 0.5 MPa utilizando los dos
métodos desarrollados en el insiso anterior. Evalue diferentes condiciones iniciales. Obtener conclusiones
a partir de los resultados.
"""
    return consigna.strip()

@router.post("/grafico-a")
def grafico_gases(params: ParametrosIniciales = Body(...)):
    resultados = calcular_volumenes_con_params(params)
    buf = generar_grafico_gases(resultados)
    return StreamingResponse(buf, media_type="image/png")

@router.post("/grafico-b")
def grafico_gas_b(params: ParametrosIniciales = Body(...)):
    P = 0.5e6
    T = 200.0
    R = 8.314
    b = params.b

    v_ideal = R * T / P

    # Intervalo adaptado como en el otro endpoint
    a_ini = b * 1.01
    b_fin = v_ideal * 10

    # VALIDACIÓN explícita del intervalo:
    if a_ini >= b_fin or a_ini <= 0 or b_fin <= 0:
       buf = generar_imagen_error_volumen()
       return StreamingResponse(buf, media_type="image/png")

    _, historial_combinado, _ = ejecutar_metodos_con_comparacion(
        a=a_ini,
        b=b_fin,
        P=P,
        T=T,
        tol=params.tol,
        max_iter=params.max_iter,
        a_vdw=params.a,
        b_vdw=params.b
    )

    if not historial_combinado:
        buf = generar_imagen_error_volumen()
        return StreamingResponse(buf, media_type="image/png")

    v_real = historial_combinado[-1]["x"]

    return generar_grafico_general(v_ideal, v_real, P, T)

@router.post("/zoom")
def grafico_zoom_gas(params: ParametrosIniciales = Body(...)):
    P = 0.5e6
    T = 200.0
    R = 8.314
    b = params.b

    v_ideal = R * T / P

    a_ini = b * 1.01
    b_fin = v_ideal * 10

    _, historial_combinado, _ = ejecutar_metodos_con_comparacion(
        a=a_ini,
        b=b_fin,
        P=P,
        T=T,
        tol=params.tol,
        max_iter=params.max_iter,
        a_vdw=params.a,
        b_vdw=params.b
    )

    if not historial_combinado:
        buf = generar_imagen_error_volumen()
        return StreamingResponse(buf, media_type="image/png")

    # FILTRO coherente
    candidatas = sorted(
        (step for step in historial_combinado if abs(step.get("fx", float("inf"))) < 1e3),
        key=lambda s: abs(s["fx"])
    )

    v_real = None
    for step in candidatas:
        xr = step["x"]
        fx = abs(step["fx"])
        if fx < 1e-4 and 0.8 < xr / v_ideal < 1.2:  # criterios para baja presión
            v_real = xr
            break

    if v_real is None:
        buf = generar_imagen_error_volumen()
        return StreamingResponse(buf, media_type="image/png")

    return generar_grafico_zoom(v_real, P, T)
 
@router.post("/taylor-vdw", response_class=PlainTextResponse)
def aplicar_taylor_vdw(params: ParametrosIniciales = Body(...)):
    return comparar_metodos_vdw(
        P=0.5e6,
        T=200.0,
        a_vdw=params.a,
        b_vdw=params.b,
        tol=params.tol,
        max_iter=params.max_iter
    ) 
 
@router.get("/explicacion-inciso-a", response_class=PlainTextResponse)
def obtener_explicacion_inciso_a():
    return EXPLICACION_INCISO_A

@router.get("/grafico_comparativo_gral")
def grafico_comparativo_gral():
    return StreamingResponse(generar_grafico_comparativo_gral(), media_type="image/png")

@router.get("/grafico_comparativo_z")
def grafico_comparativo_z():
    return StreamingResponse(generar_grafico_comparativo_z(), media_type="image/png")
 
@router.get("/dificultad-a", response_class=PlainTextResponse)
def obtener_dificultada():
    return PROBLEMAS_INCISO_A
 
@router.get("/dificultad-b", response_class=PlainTextResponse)
def obtener_dificultadb():
    return PROBLEMAS_INCISO_B
 
@router.get("/grafico_comparacion_volumenes", response_class=Response)
def grafico_comparacion_volumenes():
    imagen = generar_grafico_volumenes_comparados()
    return Response(content=imagen.getvalue(), media_type="image/png")
 

# Cambio en la resolución del item b y valores coherentes para el CO2
"""
ENCUENTRA RAICES
{
  "a": 0.364,
  "b": 0.00004267,
  "tol": 0.000001,
  "max_iter": 50
}
{
  "a": 0.4,
  "b": 0.00005,
  "tol": 0.000001,
  "max_iter": 50
}
{
  "a": 0.35,
  "b": 0.000045,
  "tol": 0.000001,
  "max_iter": 50
}
{
  "a": 0.39,
  "b": 0.000048,
  "tol": 0.000001,
  "max_iter": 50
}
{
  "a": 0.37,
  "b": 0.000046,
  "tol": 0.000001,
  "max_iter": 50
}
NO TENDRÍA RAICES VÁLIDAS
{
  "a": 0.0001,
  "b": 1.0,
  "tol": 0.000001,
  "max_iter": 50
}
{
      "a": 0.00001,
   "b": 0.1,
   "tol": 0.000001,
   "max_iter": 50
}
{
  "a": 1e-4,
  "b": 1e-2,
  "tol": 1e-6,
  "max_iter": 50
}


"""
@router.post("/resultado")
def resultado_taylor_05mpa(params: ParametrosIniciales):
    return resolver_resultado_gas(params, P=0.5e6, T=200.0)

@router.get("/grafico-f-vdw")
def grafico_f_vdw():
    buf = generar_grafico_f_vdw()
    return StreamingResponse(buf, media_type="image/png")