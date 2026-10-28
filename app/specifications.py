class Specification:
    def is_satisfied_by(self, order):
        raise NotImplementedError
    
    def __and__(self, other):
        return AndSpec(self, other)
    def __or__(self, other):
        return OrSpec(self, other)
    def __invert__(self):
        return NotSpec(self)
    
class AndSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right
    def is_satisfied_by(self, order):
        return (self.left.is_satisfied_by(order)
                and self.right.is_satisfied_by(order))
        
        
class OrSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right
    def is_satisfied_by(self, order):
        return (self.left.is_satisfied_by(order)
                or self.right.is_satisfied_by(order))
        
        
# class NotSpec(Specification):
#     def __init__(self, left, right):
#         self.left, self.right = left, right
        
#     def is_satisfied_by(self, order):
#         return (self.left.is_satisfied_by(order)
#                 not self.right.is_satisfied_by(order))

class NotSpec(Specification):
    # Solo recibe una especificación, no un 'left' y 'right'
    def __init__(self, spec):
        self.spec = spec
        
    def is_satisfied_by(self, order):
        # Se aplica el 'not' a la única especificación guardada
        return not self.spec.is_satisfied_by(order)        

        
# Completa OrSpec y NotSpec siguiendo el mismo patrón.

from decimal import Decimal


class MinimumAmountSpec(Specification):
    def __init__(self, min_amount: Decimal):
        self.min_amount = min_amount
        
    def is_satisfied_by(self, order):
        # La instrucción requiere usar estrictamente ">", no ">="[cite: 5].
        return order.total.amount > self.min_amount

class VIPCustomerSpec(Specification):
    def is_satisfied_by(self, order):
        return order.customer.is_vip

class MinimumUnitsSpec(Specification):
    def __init__(self, min_units: int):
        self.min_units = min_units
        
    def is_satisfied_by(self, order):
        # Debe exigir al menos la cantidad de unidades indicadas[cite: 5].
        return order.units >= self.min_units

class ActivePromotionSpec(Specification):
    def is_satisfied_by(self, order):
        return order.has_promotion

# Regla de descuento de 10 %:
ten_percent = (
 MinimumAmountSpec(Decimal("500"))
 & VIPCustomerSpec()
 & MinimumUnitsSpec(4)
 & ~ActivePromotionSpec()
)
# Regla de 5 %: total > 5000 y SIN promoción.
five_percent = (
    MinimumAmountSpec(Decimal("5000"))
    & ~ActivePromotionSpec()
)
# Combina ambas reglas con OR.
# Si ambas se cumplen, aplica primero 10 %.

any_discount_rule = ten_percent | five_percent

