import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import JsonResponse

from .models import Product, ProductImage, BankAccount, Customer, Order, OrderItem, CompanyProfile
from .forms import (
    ProductForm, CompanyProfileForm, BankAccountForm,
    StaffUserCreateForm, StaffUserEditForm,
    CustomerAdminForm, AdminOrderCreateForm
)
from .decorators import dashboard_admin_required


# --- AUTH ADMIN / STAFF ---

def dashboard_login(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('dashboard_index')

    next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard_index'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active and (user.is_staff or user.is_superuser):
                login(request, user)
                messages.success(request, f'Selamat datang kembali di Dashboard, {user.get_full_name() or user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Akun ini tidak memiliki hak akses staff ke Dashboard Admin.')
        else:
            messages.error(request, 'Username atau password admin tidak valid.')

    return render(request, 'core/dashboard/login.html', {
        'next': next_url,
    })


def dashboard_logout(request):
    logout(request)
    messages.info(request, 'Anda telah keluar dari Dashboard Admin.')
    return redirect('dashboard_login')


# --- DASHBOARD OVERVIEW ---

@dashboard_admin_required
def dashboard_index(request):
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_gallery_images = ProductImage.objects.count()
    total_staff = User.objects.filter(is_staff=True).count()
    
    recent_products = Product.objects.all().order_by('-created_at')[:6]
    profile = CompanyProfile.objects.first()

    return render(request, 'core/dashboard/index.html', {
        'total_products': total_products,
        'active_products': active_products,
        'total_gallery_images': total_gallery_images,
        'total_staff': total_staff,
        'recent_products': recent_products,
        'profile': profile,
    })


# --- CRUD PRODUK ---

@dashboard_admin_required
def dashboard_product_list(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.all().order_by('-created_at')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'core/dashboard/products/list.html', {
        'products': products,
        'query': query,
    })


@dashboard_admin_required
def dashboard_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            images = request.FILES.getlist('gallery_images')
            for idx, img_file in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=img_file,
                    order=idx
                )
            messages.success(request, f'Produk "{product.name}" berhasil ditambahkan!')
            return redirect('dashboard_product_list')
    else:
        form = ProductForm()

    return render(request, 'core/dashboard/products/form.html', {
        'form': form,
        'action_title': 'Tambah Produk Baru',
        'is_edit': False,
    })


@dashboard_admin_required
def dashboard_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            images = request.FILES.getlist('gallery_images')
            start_order = product.gallery_images.count()
            for idx, img_file in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=img_file,
                    order=start_order + idx
                )
            messages.success(request, f'Produk "{product.name}" berhasil diperbarui!')
            return redirect('dashboard_product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'core/dashboard/products/form.html', {
        'form': form,
        'product': product,
        'action_title': f'Edit Produk: {product.name}',
        'is_edit': True,
    })


@dashboard_admin_required
@require_POST
def dashboard_product_image_delete(request, pk):
    image = get_object_or_404(ProductImage, pk=pk)
    product_id = image.product.id
    if image.image:
        image.image.delete(save=False)  # Hapus file fisik
    image.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Foto berhasil dihapus.'})
    messages.success(request, 'Foto galeri berhasil dihapus.')
    return redirect('dashboard_product_edit', product_id=product_id)


@dashboard_admin_required
def dashboard_product_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save()
    status_str = "diaktifkan" if product.is_active else "dinonaktifkan"
    messages.success(request, f'Status produk "{product.name}" berhasil {status_str}.')
    return redirect('dashboard_product_list')


@dashboard_admin_required
def dashboard_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Produk "{name}" berhasil dihapus.')
        return redirect('dashboard_product_list')

    return render(request, 'core/dashboard/products/delete.html', {
        'product': product,
    })


# --- CRUD TRANSAKSI / ORDER ---

@dashboard_admin_required
def dashboard_order_list(request):
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    orders = Order.objects.select_related('customer', 'selected_bank').order_by('-created_at')

    if status_filter in ['pending', 'confirmed', 'rejected']:
        orders = orders.filter(status=status_filter)

    if search_query:
        orders = orders.filter(
            Q(order_code__icontains=search_query) |
            Q(recipient_name__icontains=search_query) |
            Q(recipient_phone__icontains=search_query)
        )

    # Counts for tab badges
    pending_count = Order.objects.filter(status='pending').count()
    confirmed_count = Order.objects.filter(status='confirmed').count()
    rejected_count = Order.objects.filter(status='rejected').count()
    all_count = Order.objects.count()

    return render(request, 'core/dashboard/orders/list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'rejected_count': rejected_count,
        'all_count': all_count,
    })


@dashboard_admin_required
def dashboard_order_detail(request, order_id):
    order = get_object_or_404(Order.objects.select_related('customer', 'selected_bank'), id=order_id)
    items = order.items.select_related('product').all()

    return render(request, 'core/dashboard/orders/detail.html', {
        'order': order,
        'items': items,
    })


@dashboard_admin_required
@require_POST
def dashboard_order_status_update(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    if new_status in ['pending', 'confirmed', 'rejected']:
        order.status = new_status
        order.save()
        messages.success(request, f'Status pesanan #{order.order_code} berhasil diubah menjadi "{order.get_status_display()}".')
    else:
        messages.error(request, 'Status pesanan tidak valid.')
    return redirect('dashboard_order_detail', order_id=order.id)


@dashboard_admin_required
def dashboard_order_create(request):
    products = Product.objects.filter(is_active=True).order_by('name')
    if request.method == 'POST':
        form = AdminOrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            today_str = timezone.now().strftime('%Y%m%d')
            order_code = f"SMS-{today_str}-{uuid.uuid4().hex[:4].upper()}"
            while Order.objects.filter(order_code=order_code).exists():
                order_code = f"SMS-{today_str}-{uuid.uuid4().hex[:4].upper()}"

            order.order_code = order_code
            order.status = 'confirmed'
            order.total_amount = Decimal('0.00')
            order.save()

            # Process multiple items if provided via POST lists
            product_ids = request.POST.getlist('product_ids[]')
            quantities = request.POST.getlist('quantities[]')

            total_amount = Decimal('0.00')
            has_items = False

            if product_ids and quantities and len(product_ids) == len(quantities):
                for p_id, q_val in zip(product_ids, quantities):
                    try:
                        p_obj = Product.objects.get(id=p_id, is_active=True)
                        q_int = max(1, int(q_val))
                        item_subtotal = p_obj.price * q_int
                        total_amount += item_subtotal
                        OrderItem.objects.create(
                            order=order,
                            product=p_obj,
                            quantity=q_int,
                            price=p_obj.price
                        )
                        has_items = True
                    except (Product.DoesNotExist, ValueError, TypeError):
                        continue

            if not has_items:
                primary_product = form.cleaned_data['product']
                primary_qty = form.cleaned_data['quantity']
                total_amount = primary_product.price * primary_qty
                OrderItem.objects.create(
                    order=order,
                    product=primary_product,
                    quantity=primary_qty,
                    price=primary_product.price
                )

            order.total_amount = total_amount
            order.save()

            messages.success(request, f'Transaksi walk-in #{order.order_code} senilai {order.formatted_total} berhasil dicatat dan dikonfirmasi!')
            return redirect('dashboard_order_detail', order_id=order.id)
        else:
            messages.error(request, 'Mohon periksa kembali formulir pesanan walk-in.')
    else:
        form = AdminOrderCreateForm()

    return render(request, 'core/dashboard/orders/create.html', {
        'form': form,
        'products': products,
    })


@dashboard_admin_required
def dashboard_order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        code = order.order_code
        order.delete()
        messages.success(request, f'Pesanan #{code} berhasil dihapus.')
        return redirect('dashboard_order_list')

    return render(request, 'core/dashboard/orders/delete.html', {
        'order': order,
    })


# --- CRUD PENGATURAN PUBLIK (CompanyProfile) ---

@dashboard_admin_required
def dashboard_settings(request):
    profile = CompanyProfile.objects.first()
    if not profile:
        profile = CompanyProfile.objects.create(hero_title='CV. Setia Makmur Surabaya')

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Profil Perusahaan berhasil disimpan!')
            return redirect('dashboard_settings')
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'core/dashboard/settings/company_profile.html', {
        'form': form,
        'profile': profile,
    })


# --- CRUD REKENING TUJUAN TRANSFER ---

@dashboard_admin_required
def dashboard_bank_list(request):
    banks = BankAccount.objects.all().order_by('id')
    return render(request, 'core/dashboard/banks/list.html', {
        'banks': banks,
    })


@dashboard_admin_required
def dashboard_bank_create(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            bank = form.save()
            messages.success(request, f'Rekening {bank.bank_name} berhasil ditambahkan!')
            return redirect('dashboard_bank_list')
    else:
        form = BankAccountForm()

    return render(request, 'core/dashboard/banks/form.html', {
        'form': form,
        'action_title': 'Tambah Rekening Bank Baru',
        'is_edit': False,
    })


@dashboard_admin_required
def dashboard_bank_edit(request, bank_id):
    bank = get_object_or_404(BankAccount, id=bank_id)
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rekening {bank.bank_name} berhasil diperbarui!')
            return redirect('dashboard_bank_list')
    else:
        form = BankAccountForm(instance=bank)

    return render(request, 'core/dashboard/banks/form.html', {
        'form': form,
        'bank': bank,
        'action_title': f'Edit Rekening: {bank.bank_name}',
        'is_edit': True,
    })


@dashboard_admin_required
def dashboard_bank_toggle(request, bank_id):
    bank = get_object_or_404(BankAccount, id=bank_id)
    bank.is_active = not bank.is_active
    bank.save()
    status_str = "diaktifkan" if bank.is_active else "dinonaktifkan"
    messages.success(request, f'Rekening {bank.bank_name} ({bank.account_number}) berhasil {status_str}.')
    return redirect('dashboard_bank_list')


@dashboard_admin_required
def dashboard_bank_delete(request, bank_id):
    bank = get_object_or_404(BankAccount, id=bank_id)
    if request.method == 'POST':
        name = f"{bank.bank_name} - {bank.account_number}"
        try:
            bank.delete()
            messages.success(request, f'Rekening {name} berhasil dihapus.')
        except Exception:
            messages.error(request, f'Rekening {name} tidak dapat dihapus karena sudah memiliki riwayat transaksi terkait.')
        return redirect('dashboard_bank_list')

    return render(request, 'core/dashboard/banks/delete.html', {
        'bank': bank,
    })


# --- CRUD DATA PELANGGAN ---

@dashboard_admin_required
def dashboard_customer_list(request):
    query = request.GET.get('q', '').strip()
    customers = Customer.objects.annotate(orders_count=Count('orders')).order_by('-created_at')

    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )

    return render(request, 'core/dashboard/customers/list.html', {
        'customers': customers,
        'query': query,
    })


@dashboard_admin_required
def dashboard_customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    orders = customer.orders.select_related('selected_bank').order_by('-created_at')
    total_spent = orders.filter(status='confirmed').aggregate(total=Sum('total_amount'))['total'] or 0

    try:
        formatted_spent = f"Rp {int(total_spent):,}".replace(",", ".")
    except Exception:
        formatted_spent = f"Rp {total_spent}"

    return render(request, 'core/dashboard/customers/detail.html', {
        'customer': customer,
        'orders': orders,
        'total_spent': total_spent,
        'formatted_spent': formatted_spent,
    })


@dashboard_admin_required
def dashboard_customer_create(request):
    if request.method == 'POST':
        form = CustomerAdminForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Pelanggan "{customer.name}" berhasil didaftarkan!')
            return redirect('dashboard_customer_list')
    else:
        form = CustomerAdminForm()

    return render(request, 'core/dashboard/customers/form.html', {
        'form': form,
        'action_title': 'Tambah Pelanggan Baru',
        'is_edit': False,
    })


@dashboard_admin_required
def dashboard_customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerAdminForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Data pelanggan "{customer.name}" berhasil diperbarui!')
            return redirect('dashboard_customer_list')
    else:
        form = CustomerAdminForm(instance=customer)

    return render(request, 'core/dashboard/customers/form.html', {
        'form': form,
        'customer': customer,
        'action_title': f'Edit Pelanggan: {customer.name}',
        'is_edit': True,
    })


@dashboard_admin_required
def dashboard_customer_delete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        name = customer.name
        try:
            customer.delete()
            messages.success(request, f'Pelanggan "{name}" berhasil dihapus.')
        except Exception:
            messages.error(request, f'Pelanggan "{name}" tidak dapat dihapus karena sudah memiliki riwayat pesanan.')
        return redirect('dashboard_customer_list')

    return render(request, 'core/dashboard/customers/delete.html', {
        'customer': customer,
    })


@dashboard_admin_required
def dashboard_customer_toggle(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.is_active = not customer.is_active
    customer.save()
    status_str = "diaktifkan" if customer.is_active else "dinonaktifkan"
    messages.success(request, f'Akun pelanggan {customer.name} berhasil {status_str}.')
    return redirect('dashboard_customer_list')


# --- CRUD USER INTERNAL (Staff / Admin) ---

@dashboard_admin_required
def dashboard_user_list(request):
    users = User.objects.all().order_by('-is_superuser', '-is_staff', 'username')
    return render(request, 'core/dashboard/users/list.html', {
        'users': users,
    })


@dashboard_admin_required
def dashboard_user_create(request):
    if request.method == 'POST':
        form = StaffUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User staf "{user.username}" berhasil dibuat!')
            return redirect('dashboard_user_list')
    else:
        form = StaffUserCreateForm(initial={'is_staff': True})

    return render(request, 'core/dashboard/users/form.html', {
        'form': form,
        'action_title': 'Tambah Pengguna Internal Baru',
        'is_edit': False,
    })


@dashboard_admin_required
def dashboard_user_edit(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = StaffUserEditForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Data pengguna "{target_user.username}" berhasil diperbarui!')
            return redirect('dashboard_user_list')
    else:
        form = StaffUserEditForm(instance=target_user)

    return render(request, 'core/dashboard/users/form.html', {
        'form': form,
        'target_user': target_user,
        'action_title': f'Edit Pengguna: {target_user.username}',
        'is_edit': True,
    })


@dashboard_admin_required
def dashboard_user_toggle(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, 'Anda tidak dapat menonaktifkan akun Anda sendiri!')
        return redirect('dashboard_user_list')

    target_user.is_active = not target_user.is_active
    target_user.save()
    status_str = "diaktifkan" if target_user.is_active else "dinonaktifkan"
    messages.success(request, f'Status user "{target_user.username}" berhasil {status_str}.')
    return redirect('dashboard_user_list')

