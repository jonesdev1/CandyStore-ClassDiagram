from typing import List, Optional


class Person:
    """Abstract base class for all people in the system."""
    
    def __init__(self, person_id: int, name: str, email: str):
        self.person_id = person_id
        self.name = name
        self.email = email

    def display_info(self):
        return f"{self.name} ({self.email})"


class User(Person):
    """Represents a registered user who can shop."""
    
    def __init__(self, user_id: int, name: str, email: str, password: str):
        super().__init__(user_id, name, email)
        self._password = password  # Protected: sensitive data
        self._orders: List["Order"] = []  # Protected: internal state
        self._cart: Optional["ShoppingCart"] = None  # Protected: internal state
        # NEW: simple status flag
        self.email_verified: bool = False

    def login(self, email: str, password: str) -> bool:
        """Authenticate the user."""
        return self.email == email and self._password == password

    # NEW: lightweight validation to keep data consistent
    def validate(self) -> None:
        if not isinstance(self.person_id, int) or self.person_id < 0:
            raise ValueError("person_id must be a non-negative int")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        if "@" not in self.email or "." not in self.email.split("@")[-1]:
            raise ValueError("email appears invalid")

    # NEW: minimal password change helper
    def change_password(self, old_password: str, new_password: str) -> bool:
        if self._password != old_password:
            return False
        if len(new_password) < 8:
            raise ValueError("new_password must be at least 8 characters")
        self._password = new_password
        return True

    def add_to_cart(self, candy: "Candy", quantity: int):
        """Add candy to shopping cart."""
        if not self._cart:
            from .newshopping import ShoppingCart
            self._cart = ShoppingCart(self)
        self._cart.add_item(candy, quantity)

    def checkout(self, payment_method: "PaymentMethod"):
        """Convert shopping cart into an order."""
        if not self._cart:
            raise ValueError("Cart is empty")
        order = self._cart.create_order(payment_method)
        self._orders.append(order)
        self._cart.clear()
        return order

    def get_orders(self) -> List["Order"]:
        """Get a copy of the user's orders."""
        return self._orders.copy()

    def get_cart(self) -> Optional["ShoppingCart"]:
        """Get the user's shopping cart."""
        return self._cart


class Staff(User):
    """Represents store employees — inherits from User."""
    
    def __init__(self, user_id: int, name: str, email: str, password: str, position: str):
        super().__init__(user_id, name, email, password)
        self.position = position

    def update_inventory(self, candy: "Candy", new_quantity: int):
        """Update the quantity of a candy in inventory."""
        candy.quantity = new_quantity

    def view_sales_report(self, orders: List["Order"]):
        """Generate a sales report from a list of orders."""
        total = sum(order.total_amount for order in orders)
        return f"Total sales: ${total:.2f}"
