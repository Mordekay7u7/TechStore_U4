# TechStore U4 - Núcleo de Negocio y API REST

Este proyecto es una implementación de la lógica de negocio para la administración de pedidos de la tienda **TechStore**, desarrollada como parte de la Actividad 4 (Unidad 4) de la materia Componentes de Lógica de Negocio en FIME, UANL.

La solución implementa el patrón **Specification**, una máquina de estados para el ciclo de vida del pedido con **Domain Events**, y expone sus operaciones mediante una API REST con **FastAPI**.

---

## 📁 Estructura del Proyecto

```text
techstore-u4/
├── datos/                  # Archivos CSV con la información base (clientes, productos, pedidos, etc.)
│   ├── clientes.csv
│   ├── productos.csv
│   ├── pedidos.csv
│   ├── detalle_pedidos.csv
│   └── escenarios.csv
├── app/                    # Módulo principal de la aplicación
│   ├── __init__.py
│   ├── domain.py           # Entidades (Order, Customer), Value Objects (Money, OrderItem) y Domain Events
│   ├── specifications.py   # Patrón Specification y reglas compuestas de descuento
│   └── api.py              # Endpoints HTTP con FastAPI
├── tests/                  # Suite de pruebas automáticas con pytest
│   ├── test_domain.py
│   └── test_api.py
├── cargar_csv.py           # Cargador de fixtures de datos en memoria
├── README.md               # Documentación del proyecto
└── .gitignore              # Archivos excluidos del control de versiones



🛠️ Requisitos Previos e Instalación
1. Clonar el repositorio
 
2. Crear y activar entorno virtual (Python 3.11+)
Windows PowerShell:
    python -m venv .venv
    .venv\Scripts\Activate.ps1

macOS / Linux:
    python3 -m venv .venv
    source .venv/bin/activate

3. Instalar dependencias
python -m pip install fastapi uvicorn pytest httpx

🚀 Ejecución del Sistema
Carga de datos inicial (Fixtures CSV)
Para verificar la lectura e inicialización de los 16 pedidos en estado DRAFT, ejecuta:
    python cargar_csv.py

Iniciar servidor API REST
Para ejecutar la API en modo de desarrollo con recarga automática:
    python -m uvicorn app.api:app --reload


Una vez iniciado el servidor:
    Documentación interactiva (Swagger UI): http://127.0.0.1:8000/docs


🧪 Ejecución de Pruebas Automáticas
Las pruebas automatizadas validan reglas de dominio, límites de unidades, especificaciones de descuento y respuestas HTTP de la API:

python -m pytest -q

🧠 Reglas de Negocio Implementadas
    Límites de Pedidos:
        Un pedido no puede superar las 20 unidades en total (suma de cantidades de sus ítems).

        Solo se permite agregar artículos si el pedido está en estado DRAFT.

        Los precios y montos se manejan exclusivamente en moneda MXN y con precisión Decimal.

    Reglas de Descuento (Specification Pattern):
        Descuento del 10%: Requiere cliente VIP (is_vip=True), monto superior a $500.00 MXN (total > 500), \
        al menos 4 unidades (units >= 4) y ausencia de promoción activa (has_promotion=False).

        Descuento del 5%: Requiere monto estrictamente mayor a $5000.00 MXN (total > 5000) y ausencia de promoción activa.

    Ciclo de Vida y Eventos de Dominio:
        DRAFT -> CONFIRMED: Método confirm(). 
        Exige cliente activo y pedido con artículos. Emite OrderConfirmed.

        CONFIRMED -> SHIPPED: Método ship(tracking_number). 
        Exige guía de envío no vacía. Emite OrderShipped.

        CONFIRMED -> CANCELLED: Método cancel(reason). 
        Exige motivo no vacío. Emite OrderCancelled.

        SHIPPED -> DELIVERED: Método deliver(). 
        Emite OrderDelivered.

        SHIPPED -> RETURNED: Método return_order(). 
        Emite OrderReturned.

🌐 Endpoints de la API REST
    GET /orders/{order_id} - Obtiene el detalle, ítems y lista de eventos de un pedido (404 si no existe).

    POST /orders/{order_id}/confirm - Confirma un pedido en estado DRAFT (409 en conflicto de estado, 422 si datos son inválidos).

    POST /orders/{order_id}/ship?tracking_number={guia} - Registra el envío de un pedido (requiere guía obligatoria).

    POST /orders/{order_id}/cancel?reason={motivo} - Cancela un pedido en estado CONFIRMED.