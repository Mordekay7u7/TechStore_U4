from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from cargar_csv import load_fixture
from app.domain import (
    Order,
    OrderItem,
    Money,
    InvalidOrderTransition,
    InvalidOrderData,
    OrderItemLimitExceeded
)

app = FastAPI(title="TechStore U4")

# Carga de fixtures en memoria al iniciar la aplicación
orders: dict[str, Order] = load_fixture()


# Esquema Pydantic para recibir ítems en la API (opcional para ampliar endpoints)
class AddItemRequest(BaseModel):
    sku: str
    quantity: int
    unit_price: Decimal


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    """Obtiene el detalle de un pedido por su ID."""
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="No existe el pedido")
    
    return {
        "id": order.id,
        "customer_id": order.customer.id,
        "status": order.status.value,
        "has_promotion": order.has_promotion,
        "units": order.units,
        "total": str(order.total.amount),
        "currency": order.total.currency,
        "items": [
            {
                "sku": item.sku,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price.amount),
                "subtotal": str(item.subtotal.amount)
            }
            for item in order.items
        ],
        "events": [
            {"name": e.name, "occurred_at": e.occurred_at.isoformat()}
            for e in order.events
        ]
    }


@app.post("/orders/{order_id}/confirm")
def confirm_order(order_id: str):
    """Confirma un pedido en estado DRAFT."""
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="No existe")
    
    try:
        order.confirm()
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidOrderData as exc:
        raise HTTPException(status_code=422, detail=str(exc))
        
    return {"id": order.id, "status": order.status.value}


@app.post("/orders/{order_id}/ship")
def ship_order(order_id: str, tracking_number: str):
    """Marca un pedido como enviado requiriendo guía de envío."""
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="No existe")
        
    try:
        order.ship(tracking_number)
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidOrderData as exc:
        raise HTTPException(status_code=422, detail=str(exc))
        
    return {"id": order.id, "status": order.status.value}


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, reason: str):
    """Cancela un pedido confirmado requiriendo motivo."""
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="No existe")
        
    try:
        order.cancel(reason)
    except InvalidOrderTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except InvalidOrderData as exc:
        raise HTTPException(status_code=422, detail=str(exc))
        
    return {"id": order.id, "status": order.status.value}