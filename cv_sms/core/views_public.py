import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse

from .models import Product, BankAccount, Order, OrderItem, Customer, CompanyProfile
from .cart import Cart
from .forms import CustomerRegistrationForm, CustomerLoginForm, CheckoutForm
from .decorators import customer_login_required

def home(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    banks = BankAccount.objects.filter(is_active=True)
    return render(request, 'core/home.html', {
        'products': products,
        'banks': banks,
    })

def cart_detail(request):
    cart = Cart(request)
    banks = BankAccount.objects.filter(is_active=True)
    return render(request, 'core/cart.html', {
        'cart': cart,
        'banks': banks,
    })

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = Cart(request)
    qty = 1
    if request.method == 'POST':
        try:
            qty = max(1, int(request.POST.get('quantity', 1)))
        except (ValueError, TypeError):
            qty = 1
    cart.add(product=product, quantity=qty)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} berhasil ditambahkan ke keranjang.',
            'cart_count': len(cart),
            'cart_total': cart.get_formatted_total(),
        })

    messages.success(request, f'"{product.name}" ({qty} {product.unit}) berhasil ditambahkan ke keranjang.')
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('cart_detail')

def cart_update(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            qty = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            qty = 1
        cart = Cart(request)
        cart.update(product_id=product_id, quantity=qty)
        messages.success(request, 'Jumlah item keranjang belanja berhasil diperbarui.')
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    messages.info(request, 'Item berhasil dihapus dari keranjang.')
    return redirect('cart_detail')

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.info(request, 'Keranjang belanja telah dikosongkan.')
    return redirect('cart_detail')

@customer_login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Keranjang belanja Anda masih kosong. Silakan pilih produk terlebih dahulu.')
        return redirect('cart_detail')

    customer = request.customer

    initial_data = {
        'recipient_name': customer.name,
        'recipient_phone': customer.phone,
        'shipping_address': customer.address,
    }

    banks = BankAccount.objects.filter(is_active=True)

    if request.method == 'POST':
        form = CheckoutForm(request.POST, request.FILES)
        if form.is_valid():
            # Generate unique order code: SMS-YYYYMMDD-XXXX
            today_str = timezone.now().strftime('%Y%m%d')
            order_code = f"SMS-{today_str}-{uuid.uuid4().hex[:4].upper()}"
            while Order.objects.filter(order_code=order_code).exists():
                order_code = f"SMS-{today_str}-{uuid.uuid4().hex[:4].upper()}"

            order = form.save(commit=False)
            order.order_code = order_code
            order.customer = customer
            order.payment_method = 'transfer'
            order.total_amount = cart.get_total_price()
            order.status = 'pending'
            order.save()

            # Create OrderItems
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price'],
                )

            # Clear cart
            cart.clear()

            messages.success(request, f'Pesanan #{order.order_code} berhasil dibuat! Admin kami akan segera memverifikasi bukti transfer Anda.')
            return redirect('order_detail', order_code=order.order_code)
        else:
            messages.error(request, 'Mohon periksa kembali formulir checkout dan pastikan bukti transfer telah diunggah.')
    else:
        form = CheckoutForm(initial=initial_data)

    return render(request, 'core/checkout.html', {
        'form': form,
        'cart': cart,
        'banks': banks,
        'customer': customer,
    })

@customer_login_required
def order_detail(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)
    
    # Verifikasi kepemilikan pesanan oleh pelanggan yang login
    if order.customer and order.customer != request.customer:
        messages.error(request, 'Anda tidak memiliki hak akses untuk melihat pesanan ini.')
        return redirect('customer_orders')

    profile = CompanyProfile.objects.first()
    
    # Pre-generate WhatsApp message link
    wa_number = profile.clean_whatsapp if profile and profile.clean_whatsapp else '6281330780729'
    wa_text = f"Halo CV. Setia Makmur Surabaya, saya ingin konfirmasi pesanan:\nNomor: {order.order_code}\nPenerima: {order.recipient_name}\nTotal: {order.formatted_total}\nMohon diproses, terima kasih."
    import urllib.parse
    wa_url = f"https://wa.me/{wa_number}?text={urllib.parse.quote(wa_text)}"

    return render(request, 'core/order_detail.html', {
        'order': order,
        'wa_url': wa_url,
    })

def customer_register(request):
    if request.session.get('customer_id'):
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.set_password(form.cleaned_data['password'])
            customer.save()

            # Set manual session
            request.session['customer_id'] = customer.id
            messages.success(request, f'Selamat datang, {customer.name}! Pendaftaran berhasil dan Anda telah masuk.')
            return redirect(next_url)
    else:
        form = CustomerRegistrationForm()

    return render(request, 'core/customer/register.html', {
        'form': form,
        'next': next_url,
    })

def customer_login(request):
    if request.session.get('customer_id'):
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier'].strip()
            password = form.cleaned_data['password']

            customer = Customer.objects.filter(
                Q(email__iexact=identifier) | Q(phone=identifier)
            ).first()

            if customer and customer.check_password(password):
                if not customer.is_active:
                    messages.error(request, 'Akun Anda dinonaktifkan oleh administrator. Silakan hubungi kami.')
                else:
                    request.session['customer_id'] = customer.id
                    messages.success(request, f'Selamat datang kembali, {customer.name}!')
                    return redirect(next_url)
            else:
                messages.error(request, 'Email / Nomor HP atau password yang Anda masukkan tidak sesuai.')
    else:
        form = CustomerLoginForm()

    return render(request, 'core/customer/login.html', {
        'form': form,
        'next': next_url,
    })

def customer_logout(request):
    request.session.pop('customer_id', None)
    messages.info(request, 'Anda telah berhasil keluar dari akun pelanggan.')
    return redirect('home')

@customer_login_required
def customer_orders(request):
    orders = Order.objects.filter(customer=request.customer).order_by('-created_at')
    return render(request, 'core/customer/orders.html', {
        'orders': orders,
    })

