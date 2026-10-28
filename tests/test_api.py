import pytest
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_16_get_order_exitosa():
    response = client.get("/orders/O001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "O001"
    assert data["status"] == "DRAFT"

def test_17_get_order_404():
    response = client.get("/orders/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "No existe el pedido"

def test_18_confirm_order_exitoso():
    response = client.post("/orders/O013/confirm")
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"

def test_19_confirm_order_422_cliente_inactivo():
    response = client.post("/orders/O003/confirm")
    assert response.status_code == 422

def test_20_confirm_order_409_doble_confirmacion():
    client.post("/orders/O013/confirm")
    response = client.post("/orders/O013/confirm")
    assert response.status_code == 409

def test_21_ship_order_sin_guia_422():
    client.post("/orders/O012/confirm")
    response = client.post("/orders/O012/ship?tracking_number=")
    assert response.status_code == 422