from django.shortcuts import render
from .models import Product, CompanyProfile, BankAccount

def home(request):
    products = Product.objects.filter(is_active=True).prefetch_related('gallery_images').order_by('-created_at')
    company_profile = CompanyProfile.objects.first()
    banks = BankAccount.objects.filter(is_active=True)
    return render(request, 'core/home.html', {
        'products': products,
        'company_profile': company_profile,
        'banks': banks,
    })
