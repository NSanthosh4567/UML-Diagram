
class User:
    def __init__(self, user_id, email):
        self.user_id = user_id
        self.email = email

    def login(self):
        pass


class Customer(User):
    def __init__(self, user_id, email):
        super().__init__(user_id, email)
        self.cart = Cart()


class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class Cart:
    def __init__(self):
        self.items = []

    def add_product(self, product):
        self.items.append(product)


class Order:
    def __init__(self, customer, products):
        self.customer = customer
        self.products = products

    def calculate_total(self):
        return sum(p.price for p in self.products)


class PaymentService:
    def pay(self, order):
        return order.calculate_total()
