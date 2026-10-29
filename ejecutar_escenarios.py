import csv
import os
from decimal import Decimal
from cargar_csv import load_fixture
from app.specifications import ten_percent, five_percent
from app.domain import (
    InvalidOrderData,
    InvalidOrderTransition,
    OrderItemLimitExceeded,
    OrderItem,
    Money,
)


def ejecutar_escenarios():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_escenarios = os.path.join(base_dir, "datos", "escenarios.csv")

    if not os.path.exists(ruta_escenarios):
        print(f"Error: No se encontró el archivo {ruta_escenarios}")
        return

    print("=" * 80)
    print(" EJECUCIÓN DE ESCENARIOS (E01 - E15) - TECHSTORE U4 ")
    print("=" * 80)

    # utf-8-sig elimina automáticamente el BOM (\ufeff) de los archivos CSV
    with open(ruta_escenarios, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            caso_id = row["caso_id"].strip()
            # Formatea para asegurar el prefijo "O" mayúscula (ejemplo: O001)
            pedido_id = "O" + row["pedido_id"].strip().replace("O", "").zfill(3)
            accion = row["accion"].strip()
            objetivo = row["objetivo"].strip()
            pista = row["pista"].strip()

            # Vuelve a cargar las fixtures para tener los datos limpios en cada escenario
            orders = load_fixture()
            order = orders.get(pedido_id)

            if not order:
                print(f"[{caso_id}] Pedido {pedido_id} no encontrado.")
                continue

            estado_inicial = order.status.value
            print(f"\n--- Caso {caso_id} (Pedido: {pedido_id}) ---")
            print(f"Objetivo: {objetivo} | Pista: {pista}")
            print(f"Estado Inicial: {estado_inicial} | Unidades: {order.units} | Total: ${order.total.amount} MXN")

            try:
                # 1. Escenarios de Evaluación de Descuentos
                if accion == "evaluar_descuento":
                    desc_10 = ten_percent.is_satisfied_by(order)
                    desc_5 = five_percent.is_satisfied_by(order)

                    if desc_10:
                        resultado = "Aplica 10% de descuento"
                    elif desc_5:
                        resultado = "Aplica 5% de descuento"
                    else:
                        resultado = "Sin descuento (0%)"

                    print(f"Acción: {accion} -> Resultado Real: {resultado}")

                # 2. Escenarios de Confirmación Simple
                elif accion == "confirmar":
                    order.confirm()
                    eventos = [e.name for e in order.events]
                    print(f"Acción: {accion} -> Resultado Real: Confirmado exitosamente.")
                    print(f"Estado Final: {order.status.value} | Eventos emitidos: {eventos}")

                # 3. Escenario E08: Agregar Ítem que excede unidades
                elif accion == "agregar SKU003 x2":
                    item_nuevo = OrderItem(
                        sku="SKU003",
                        quantity=2,
                        unit_price=Money(Decimal("120.00"))
                    )
                    order.add_item(item_nuevo)
                    print(f"Acción: {accion} -> Resultado Real: Ítem agregado. Nuevas Unidades: {order.units}")

                # 4. Escenario E11: Confirmar y Enviar sin guía
                elif accion == "confirmar y enviar sin guia":
                    order.confirm()
                    print("  - Confirmación exitosa. Intentando enviar con guía vacía...")
                    order.ship("   ")

                # 5. Escenario E12: Confirmar dos veces
                elif accion == "confirmar dos veces":
                    order.confirm()
                    print("  - Primera confirmación exitosa. Intentando segunda confirmación...")
                    order.confirm()

                # 6. Escenario E13: Confirmar, enviar y cancelar desde SHIPPED
                elif accion == "confirmar, enviar y cancelar":
                    order.confirm()
                    order.ship("GUIA-E13")
                    print("  - Confirmado y enviado exitosamente. Intentando cancelar...")
                    order.cancel("Cliente se arrepintió")

                # 7. Escenario E14: Confirmar, enviar y devolver
                elif accion == "confirmar, enviar y devolver":
                    order.confirm()
                    order.ship("GUIA-E14")
                    order.return_order()
                    eventos = [e.name for e in order.events]
                    print(f"Acción: {accion} -> Resultado Real: Devolución registrada exitosamente.")
                    print(f"Estado Final: {order.status.value} | Eventos emitidos: {eventos}")

                # 8. Escenario E15: Confirmar, enviar y entregar
                elif accion == "confirmar, enviar y entregar":
                    order.confirm()
                    order.ship("GUIA-E15")
                    order.deliver()
                    eventos = [e.name for e in order.events]
                    print(f"Acción: {accion} -> Resultado Real: Entrega registrada exitosamente.")
                    print(f"Estado Final: {order.status.value} | Eventos emitidos: {eventos}")

                else:
                    print(f"Acción '{accion}' no reconocida.")

            except (InvalidOrderData, InvalidOrderTransition, OrderItemLimitExceeded) as exc:
                print(f"Acción: {accion} -> RECHAZADO / EXCEPCIÓN: {type(exc).__name__} -> {exc}")
                print(f"Estado Final: {order.status.value} | Eventos emitidos: {[e.name for e in order.events]}")

    print("\n" + "=" * 80)
    print(" EJECUCIÓN FINALIZADA")
    print("=" * 80)


if __name__ == "__main__":
    ejecutar_escenarios()