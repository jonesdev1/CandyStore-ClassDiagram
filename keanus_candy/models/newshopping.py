from datetime import datetime
from typing import List

from .newperson import User
from .product import Candy
from .payment import PaymentMethod


class CartItem:
    """Represents a candy in the cart."""
    
    def __init__(self, candy: Candy, quantity: int):
        self.candy = candy
        self.quantity = quantity

    def subtotal(self):
        """Calculate the subtotal for this cart item."""
        return self.candy.price * self.quantity


class ShoppingCart:
    """User's temporary basket."""
    
    def __init__(self, user: User):
        self.user = user
        self._items: List[CartItem] = []  # Protected: internal state
        # NEW: optional cart-wide discount (0.0 = none)
        self._discount_rate: float = 0.0

    def add_item(self, candy: Candy, quantity: int):
        """Add candy to the shopping cart."""
        for item in self._items:
            if item.candy == candy:
                item.quantity += quantity
                return
        self._items.append(CartItem(candy, quantity))

    # NEW: quick helper
    def item_count(self) -> int:
        """Total item quantity in cart."""
        return sum(i.quantity for i in self._items)

    # NEW: set a simple discount (e.g., 0.10 = 10% off)
    def set_discount(self, rate: float) -> None:
        if rate < 0.0 or rate > 0.9:
            raise ValueError("discount rate must be between 0.0 and 0.9")
        self._discount_rate = float(rate)

    def calculate_total(self, *, round_to_cents: bool = True):
        """Calculate the total amount in the cart."""
        total = sum(item.subtotal() for item in self._items)
        # Apply discount if any
        if self._discount_rate:
            total *= (1.0 - self._discount_rate)
        # Optional rounding (defaults to two decimals)
        return round(total, 2) if round_to_cents else total

    def create_order(self, payment_method: PaymentMethod) -> "Order":
        """Create an order from the current cart contents."""
        total = self.calculate_total()
        order_items = [OrderItem(i.candy, i.quantity) for i in self._items]
        return Order(self.user, order_items, total, payment_method)

    def clear(self):
        """Clear all items from the cart."""
        self._items.clear()

    def get_items(self) -> List[CartItem]:
        """Get a copy of the cart items."""
        return self._items.copy()


class Order:
    """Represents a confirmed order."""
    
    order_counter = 1000

    def __init__(self, user: User, items: List["OrderItem"], total_amount: float, payment_method: PaymentMethod):
        self.order_id = Order.order_counter
        Order.order_counter += 1
        self.user = user
        self.items = items
        self.total_amount = total_amount
        self.payment_method = payment_method
        self.status = "Pending"
        self.timestamp = datetime.now()

    def confirm_payment(self):
        """Process payment and mark the order as paid."""
        if self.payment_method.process_payment(self.total_amount):
            self.status = "Paid"
            return True
        else:
            self.status = "Payment Failed"
            return False

    def ship_order(self):
        """Mark the order as shipped."""
        self.status = "Shipped"

    # NEW: allow cancellation prior to shipping
    def cancel(self) -> bool:
        """
        Cancel the order if it hasn't shipped.
        Returns True if cancelled.
        """
        if self.status in ("Pending", "Payment Failed"):
            self.status = "Cancelled"
            return True
        return False


class OrderItem:
    """A candy included in an order."""
    
    def __init__(self, candy: Candy, quantity: int):
        self.candy = candy
        self.quantity = quantity
        self.subtotal = candy.price * quantity
