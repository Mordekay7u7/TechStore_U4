import pytest
from decimal import Decimal
from cargar_csv import load_fixture
from app.domain import (
    Money, Customer, Order, OrderItem, OrderStatus,
    InvalidOrderData, InvalidOrderTransition, OrderItemLimitExceeded
)
from app.specifications import ten_percent, five_percent

# --- 1. Money & OrderItem (3 Pruebas) ---
def test_01_money_negativo():
    with pytest.raises(InvalidOrderData):
        Money(Decimal("-1"))

def test_02_money_monedas_distintas():
    m1 = Money(Decimal("100"), "MXN")
    m2 = Money(Decimal("100"), "USD")
    with pytest.raises(InvalidOrderData):
        m1.add(m2)

def test_03_order_item_cantidad_invalida():
    with pytest.raises(InvalidOrderData):
        OrderItem(sku="SKU001", quantity=0, unit_price=Money(Decimal("100")))

# --- 2. Carga Fixtures y Límites de Unidades (3 Pruebas) ---
def test_04_pedido_0001_inicia_draft():
    orders = load_fixture()
    assert orders["O001"].status == OrderStatus.DRAFT
    assert orders["O001"].units == 4
    assert orders["O001"].total.amount == Decimal("2100.00")

def test_05_limite_20_unidades_exactas():
    orders = load_fixture()
    assert orders["O008"].units == 20

def test_06_exceder_limite_21_unidades():
    customer = Customer(id="C001", active=True)
    order = Order(customer=customer, id="TEST01")
    item = OrderItem(sku="SKU001", quantity=21, unit_price=Money(Decimal("100")))
    with pytest.raises(OrderItemLimitExceeded):
        order.add_item(item)

# --- 3. Specifications & Descuentos (4 Pruebas) ---
def test_07_regla_descuento_vip_10_porcentaje():
    orders = load_fixture()
    assert ten_percent.is_satisfied_by(orders["O001"]) is True

def test_08_regla_descuento_5_porcentaje():
    orders = load_fixture()
    assert five_percent.is_satisfied_by(orders["O006"]) is True

def test_09_promocion_activa_bloquea_descuento():
    orders = load_fixture()
    assert ten_percent.is_satisfied_by(orders["O005"]) is False
    assert five_percent.is_satisfied_by(orders["O005"]) is False

def test_10_umbral_estricto_500_sin_descuento():
    orders = load_fixture()
    assert ten_percent.is_satisfied_by(orders["O010"]) is False

# --- 4. Estados y Eventos (5 Pruebas) ---
def test_11_confirmar_cliente_inactivo():
    orders = load_fixture()
    with pytest.raises(InvalidOrderData):
        orders["O003"].confirm()

def test_12_confirmar_pedido_vacio():
    orders = load_fixture()
    with pytest.raises(InvalidOrderData):
        orders["O007"].confirm()

def test_13_envio_sin_guia():
    orders = load_fixture()
    order = orders["O012"]
    order.confirm()
    with pytest.raises(InvalidOrderData):
        order.ship("   ")

def test_14_confirmacion_doble():
    orders = load_fixture()
    order = orders["O013"]
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED
    assert len(order.events) == 1
    with pytest.raises(InvalidOrderTransition):
        order.confirm()
    assert len(order.events) == 1

def test_15_cancelacion_desde_shipped():
    orders = load_fixture()
    order = orders["O014"]
    order.confirm()
    order.ship("GUIA123")
    with pytest.raises(InvalidOrderTransition):
        order.cancel("Motivo")