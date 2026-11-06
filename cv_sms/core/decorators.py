from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Customer

def dashboard_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Silakan login sebagai staf/admin untuk mengakses area dashboard.')
            return redirect(f"/dashboard/login/?next={request.path}")
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Akses ditolak. Akun Anda tidak memiliki hak akses dashboard.')
            return redirect('dashboard_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def customer_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        customer_id = request.session.get('customer_id')
        if not customer_id:
            messages.info(request, 'Silakan login terlebih dahulu untuk mengakses halaman ini.')
            return redirect(f"/customer/login/?next={request.path}")
        
        customer = Customer.objects.filter(id=customer_id, is_active=True).first()
        if not customer:
            request.session.pop('customer_id', None)
            messages.error(request, 'Sesi akun pelanggan tidak valid atau telah dinonaktifkan. Silakan login kembali.')
            return redirect(f"/customer/login/?next={request.path}")

        request.customer = customer
        return view_func(request, *args, **kwargs)
    return _wrapped_view

