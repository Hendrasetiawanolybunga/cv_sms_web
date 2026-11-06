from .models import Customer, CompanyProfile
from .cart import Cart

def customer_context(request):
    customer = None
    customer_id = request.session.get('customer_id')
    if customer_id:
        try:
            customer = Customer.objects.filter(id=customer_id, is_active=True).first()
            if not customer:
                request.session.pop('customer_id', None)
        except Exception:
            customer = None

    profile = CompanyProfile.objects.first()
    cart = Cart(request)

    return {
        'current_customer': customer,
        'company_profile': profile,
        'cart': cart,
        'cart_count': len(cart),
        'cart_total_price': cart.get_total_price(),
        'cart_formatted_total': cart.get_formatted_total(),
    }

