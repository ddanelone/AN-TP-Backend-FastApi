import pytest
from services.tp3.gases import ejecutar_metodos_con_comparacion

def test_ejecutar_metodos_con_comparacion_valores_basicos():
    a, b = 0.001, 0.05
    tol = 1e-6
    max_iter = 50
    P = 0.5e6
    T = 200.0

    historial_taylor, historial_combinado, log = ejecutar_metodos_con_comparacion(a, b, tol, max_iter, P, T)

    # Chequeamos que las listas no estén vacías
    assert isinstance(historial_taylor, list)
    assert len(historial_taylor) > 0
    assert isinstance(historial_combinado, list)
    assert len(historial_combinado) > 0

    # Chequeamos que log sea string y contenga texto
    assert isinstance(log, str)
    assert "Iteraciones" in log

    # Últimos valores de x deben ser números (float)
    assert isinstance(historial_taylor[-1]["x"], float)
    assert isinstance(historial_combinado[-1]["x"], float)

@pytest.mark.parametrize("max_iter", [1, 5, 10])
def test_ejecutar_metodos_con_comparacion_varios_max_iter(max_iter):
    a, b = 0.001, 0.05
    tol = 1e-6
    P = 0.5e6
    T = 200.0

    historial_taylor, historial_combinado, log = ejecutar_metodos_con_comparacion(a, b, tol, max_iter, P, T)
    
    assert len(historial_taylor) <= max_iter
    assert len(historial_combinado) <= max_iter

def test_intervalo_pequeno():
    hist_taylor, hist_combinado, log = ejecutar_metodos_con_comparacion(a=1.0, b=1.00001, tol=1e-6, max_iter=10, P=0.5e6, T=200)
    assert len(hist_taylor) <= 10
    assert "Comparación de rendimiento" in log
    assert abs(hist_taylor[-1]["error"]) < 1e-4  # tolerancia más relajada por intervalo pequeño
