from decimal import Decimal
from .models import Product

CART_SESSION_ID = 'cart'

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        quantity = max(1, int(quantity))
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def update(self, product_id, quantity):
        product_id = str(product_id)
        quantity = int(quantity)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.remove(product_id)
            self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.session.modified = True

    def save(self):
        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True

    def __iter__(self):
        product_ids = [int(pid) for pid in self.cart.keys() if pid.isdigit()]
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        products_map = {p.id: p for p in products}

        # Clean up products that were deleted or made inactive
        current_keys = list(self.cart.keys())
        for pid_str in current_keys:
            if int(pid_str) not in products_map:
                del self.cart[pid_str]
        self.save()

        for pid_str, item in self.cart.items():
            product = products_map[int(pid_str)]
            price = Decimal(item['price'])
            quantity = item['quantity']
            subtotal = price * quantity
            try:
                formatted_subtotal = f"Rp {int(subtotal):,}".replace(",", ".")
            except Exception:
                formatted_subtotal = f"Rp {subtotal}"
            try:
                formatted_price = f"Rp {int(price):,}".replace(",", ".")
            except Exception:
                formatted_price = f"Rp {price}"

            yield {
                'product': product,
                'product_id': product.id,
                'quantity': quantity,
                'price': price,
                'formatted_price': formatted_price,
                'subtotal': subtotal,
                'formatted_subtotal': formatted_subtotal,
            }

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        total = Decimal('0.00')
        product_ids = [int(pid) for pid in self.cart.keys() if pid.isdigit()]
        products_map = {p.id: p for p in Product.objects.filter(id__in=product_ids, is_active=True)}
        for pid_str, item in self.cart.items():
            if int(pid_str) in products_map:
                total += Decimal(item['price']) * item['quantity']
        return total

    def get_formatted_total(self):
        total = self.get_total_price()
        try:
            return f"Rp {int(total):,}".replace(",", ".")
        except Exception:
            return f"Rp {total}"

    @property
    def items_list(self):
        return list(self.__iter__())

