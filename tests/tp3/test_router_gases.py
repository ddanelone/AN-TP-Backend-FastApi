# para ejecutar las pruebas, donde está el archivo main.py, hacemos:
# pytest tests/tp3/test_router_gases.py

import time
import pytest
from fastapi.testclient import TestClient
from main import app  
client = TestClient(app)

def test_resultado_taylor_post():
    # Parámetros válidos para enviar en el body JSON
    payload = {
        "a": 0.001,
        "b": 0.05,
        "tol": 1e-6,
        "max_iter": 50
    }

    response = client.post("/api/tp3/gases/resultado", json=payload)

    # Verificamos código HTTP 200
    assert response.status_code == 200

    data = response.json()

    # Verificamos claves esperadas
    assert "volumen_taylor" in data
    assert "volumen_combinado" in data
    assert "volumen_ideal" in data
    assert "log" in data

    # Opcional: verificar que los valores no sean None o string vacíos
    assert data["volumen_taylor"] != ""
    assert data["log"] != ""

def test_resultado_taylor_post_valido():
    payload = {
        "a": 0.001,
        "b": 0.05,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/resultado", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "volumen_taylor" in data
    assert data["volumen_taylor"] != ""

def test_resultado_taylor_post_falta_parametro():
    payload = {
        "b": 0.05,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/resultado", json=payload)

    assert response.status_code == 422  # error validación de Pydantic

def test_resultado_taylor_post_valor_negativo():
    payload = {
        "a": -0.01,
        "b": 0.05,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/resultado", json=payload)
    assert response.status_code == 422  # error validación de Pydantic

def test_resultado_taylor_post_tipo_invalido():
    payload = {
        "a": "no_numero",
        "b": 0.05,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/resultado", json=payload)
    assert response.status_code == 422  # error validación de Pydantic
    
def test_grafico_a_post_valido():
    payload = {
        "a": 0.001,
        "b": 0.05,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-a", json=payload)

    # Código 200 y tipo de contenido imagen PNG
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    # Opcional: verificar que la respuesta no esté vacía
    assert len(response.content) > 0

def test_grafico_a_post_falta_parametro():
    payload = {
        "b": 0.05,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-a", json=payload)
    assert response.status_code == 422  # Error de validación por falta de "a"

def test_grafico_a_post_valor_negativo():
    payload = {
        "a": -0.001,
        "b": 0.05,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-a", json=payload)
    assert response.status_code == 422  # Validación falla por valor negativo

def test_grafico_a_post_tipo_invalido():
    payload = {
        "a": "no_numero",
        "b": 0.05,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-a", json=payload)
    assert response.status_code == 422  # Validación falla por tipo inválido    
    
def test_grafico_zoom_post():
    payload = {
        "a": 0.364,
        "b": 0.00004267,
        "tol": 0.000001,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/zoom", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_taylor_vdw_valido():
    payload = {
        "a": 0.364,
        "b": 0.00004267,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/taylor-vdw", json=payload)
    assert response.status_code == 200
    text = response.text
    assert "Método de Taylor" in text
    assert "Método combinado" in text
    assert "Volumen ideal" in text
    assert "Diferencia Taylor" in text


def test_taylor_vdw_parametros_extremos_validos():
    payload = {
        "a": 0.364,
        "b": 0.00004267,
        "tol": 1e-12,
        "max_iter": 500
    }
    response = client.post("/api/tp3/gases/taylor-vdw", json=payload)
    assert response.status_code == 200
    text = response.text
    assert "Método de Taylor" in text
    assert "log" in text or "Volumen ideal" in text  # contenido esperado


# --- Casos de error controlado dentro del endpoint (lógica interna, pero parámetros válidos) ---

def test_taylor_vdw_intervalo_invalido():
    payload = {
        "a": 1000.0,
        "b": 50.0,  # a > b → intervalo inválido
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/taylor-vdw", json=payload)
    assert response.status_code == 200
    assert "Intervalo inicial inválido" in response.text


def test_taylor_vdw_timeout_fuerza_error():
    payload = {
        "a": 1e6,
        "b": 1e5,
        "tol": 1e-12,
        "max_iter": 500
    }
    response = client.post("/api/tp3/gases/taylor-vdw", json=payload)
    assert response.status_code == 200
    text = response.text
    assert (
        "Error al aplicar los métodos" in text
        or "Intervalo inicial inválido" in text
    )



# --- Casos inválidos por validación (Pydantic 422) ---

def test_taylor_vdw_faltan_parametros():
    payload = {
        "a": 0.364,
        # Falta "b"
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/taylor-vdw", json=payload)
    assert response.status_code == 422


def test_taylor_vdw_parametros_invalidos():
    payload = {
        "a": 1e6,
        "b": 1e5,
        "tol": 1e-20,      # demasiado chico (puede evaluarse como 0)
        "max_iter": 1000   # fuera de rango (> 500)
    }
    response = client.post("/api/tp3/gases/taylor-vdw", json=payload)
    assert response.status_code == 422


def test_taylor_vdw_valores_invalidos_rechazados():
    payload = {
        "a": -1.0,
        "b": -1.0,
        "tol": 1e-20,
        "max_iter": 500
    }
    response = client.post("/api/tp3/gases/taylor-vdw", json=payload)
    assert response.status_code == 422
    
# TEST DE INTEGRACIÓN
def test_grafico_b_post_valido2():
    payload = {
        "a": 0.001,
        "b": 0.0000427,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-b", json=payload)
    assert response.status_code == 200
    # Es una imagen PNG, chequeamos el content-type
    assert response.headers["content-type"] == "image/png"
    # El contenido no está vacío
    assert len(response.content) > 1000

def test_grafico_b_post_falta_parametro():
    payload = {
        "b": 0.0000427,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-b", json=payload)
    assert response.status_code == 422

def test_grafico_b_post_parametro_negativo():
    payload = {
        "a": -0.001,
        "b": 0.0000427,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-b", json=payload)
    assert response.status_code == 422

def test_grafico_b_post_intervalo_invalido():
    payload = {
        "a": 1000,  # muy grande para que el intervalo sea inválido
        "b": 500,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-b", json=payload)
    assert response.status_code == 200

    content_type = response.headers.get("content-type", "")
    
    # ✅ Ahora esperamos imagen, no JSON
    assert "image/png" in content_type, f"Se esperaba PNG, pero Content-Type fue: {content_type}"

    # ✅ Confirmamos que se recibió contenido
    assert response.content is not None
    assert len(response.content) > 100, "La imagen parece estar vacía o es muy pequeña"


def test_grafico_b_post_valido():
    payload = {
        "a": 1e-5,      # valores válidos, intervalo correcto
        "b": 1e-6,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-b", json=payload)
    assert response.status_code == 200

    content_type = response.headers.get("content-type", "")
    
    # En caso válido, esperamos una imagen PNG
    assert "image/png" in content_type, f"Se esperaba image/png, pero Content-Type fue: {content_type}"

    # Podés validar que el contenido no está vacío
    assert response.content is not None
    assert len(response.content) > 100  # arbitrario, para chequear que hay contenido de imagen

def test_grafico_b_post_performance():
    payload = {
        "a": 0.001,
        "b": 0.0000427,
        "tol": 1e-6,
        "max_iter": 50
    }
    start = time.perf_counter()
    response = client.post("/api/tp3/gases/grafico-b", json=payload)
    end = time.perf_counter()
    assert response.status_code == 200
    elapsed = end - start
    # Asumimos que tarda menos de 2 segundos (ajustá según necesidad)
    assert elapsed < 2.0

def test_resultado_post_y_get():
    payload = {
        "a": 0.001,
        "b": 0.0000427,
        "tol": 1e-6,
        "max_iter": 50
    }
    post_resp = client.post("/api/tp3/gases/resultado", json=payload)
    assert post_resp.status_code == 200
    data_post = post_resp.json()
    assert "volumen_taylor" in data_post

    # Supongamos que GET /resultado/{id} existe y devuelve detalle
    # id = data_post["id"]
    # get_resp = client.get(f"/api/tp3/gases/resultado/{id}")
    # assert get_resp.status_code == 200
    # data_get = get_resp.json()
    # assert data_get == data_post


@pytest.mark.parametrize("payload, expected_status", [
    ({"a": 0.001, "b": 0.0000427, "tol": 1e-6, "max_iter": 50}, 200),
    ({"a": -0.01, "b": 0.0000427, "tol": 1e-6, "max_iter": 50}, 422),  # a negativo
    ({"a": 0.001, "b": -0.0001, "tol": 1e-6, "max_iter": 50}, 422),   # b negativo
    ({"a": 0.001, "b": 0.0000427, "tol": -1e-6, "max_iter": 50}, 422), # tol negativo
    ({"a": 0.001, "b": 0.0000427, "tol": 1e-6, "max_iter": 0}, 422),   # max_iter fuera de rango
])
def test_grafico_b_post_parametrizado(payload, expected_status):
    response = client.post("/api/tp3/gases/grafico-b", json=payload)
    assert response.status_code == expected_status

def test_grafico_b_post_contenido_imagen():
    payload = {
        "a": 0.001,
        "b": 0.0000427,
        "tol": 1e-6,
        "max_iter": 50
    }
    response = client.post("/api/tp3/gases/grafico-b", json=payload)
    assert response.status_code == 200
    content = response.content
    # PNG empieza con bytes 89 50 4E 47
    assert content[:4] == b"\x89PNG"
