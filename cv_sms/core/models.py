import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password, check_password


class CompanyProfile(models.Model):
    hero_title = models.CharField(max_length=255, default='CV. Setia Makmur Surabaya')
    hero_subtitle = models.TextField(blank=True, default='Penyedia Kain Majun, Sarung Tangan, Tali Rafia, Masker, & Mesin Industri Berkualitas.')
    about_text = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone_office = models.CharField(max_length=50, blank=True)
    phone_whatsapp = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    hero_image = models.ImageField(upload_to='company/', blank=True, null=True)

    class Meta:
        verbose_name = 'Profil Perusahaan'
        verbose_name_plural = 'Profil Perusahaan'

    def __str__(self):
        return self.hero_title

    @property
    def clean_whatsapp(self):
        if not self.phone_whatsapp:
            return ""
        # Remove non-digits
        digits = "".join(ch for ch in self.phone_whatsapp if ch.isdigit())
        if digits.startswith("0"):
            digits = "62" + digits[1:]
        elif digits.startswith("8"):
            digits = "62" + digits
        return digits


class BankAccount(models.Model):
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_holder = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Rekening Bank'
        verbose_name_plural = 'Daftar Rekening Bank'
        ordering = ['id']

    def __str__(self):
        return f"{self.bank_name} - {self.account_number} a.n. {self.account_holder}"


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg', help_text='Contoh: kg, lusin, unit, roll')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Produk'
        verbose_name_plural = 'Daftar Produk'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            candidate = base_slug
            num = 1
            while Product.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{num}"
                num += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def formatted_price(self):
        try:
            return f"Rp {int(self.price):,}".replace(",", ".")
        except (ValueError, TypeError):
            return f"Rp {self.price}"

    @property
    def all_images(self):
        """Mengembalikan list seluruh URL gambar (foto utama + galeri)"""
        images = []
        if self.image:
            images.append({'url': self.image.url, 'caption': self.name, 'is_cover': True})
        for img in self.gallery_images.all():
            if img.image:
                images.append({'url': img.image.url, 'caption': img.caption or self.name, 'is_cover': False})
        return images


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')
    caption = models.CharField(max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Foto Galeri Produk'
        verbose_name_plural = 'Foto Galeri Produk'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} - Gallery #{self.id}"


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pelanggan'
        verbose_name_plural = 'Data Pelanggan'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Menunggu Konfirmasi'),
        ('confirmed', 'Dikonfirmasi'),
        ('rejected', 'Ditolak'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('transfer', 'Transfer Bank'),
        ('cash_walkin', 'Tunai / Walk-in'),
    )

    order_code = models.CharField(max_length=32, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    recipient_name = models.CharField(max_length=150)
    recipient_phone = models.CharField(max_length=30)
    shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    selected_bank = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='transfer')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pesanan'
        verbose_name_plural = 'Daftar Pesanan'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_code} - {self.recipient_name}"

    @property
    def formatted_total(self):
        try:
            return f"Rp {int(self.total_amount):,}".replace(",", ".")
        except (ValueError, TypeError):
            return f"Rp {self.total_amount}"

    @property
    def status_badge_class(self):
        if self.status == 'confirmed':
            return 'bg-emerald-100 text-emerald-800 border-emerald-300'
        elif self.status == 'rejected':
            return 'bg-rose-100 text-rose-800 border-rose-300'
        return 'bg-amber-100 text-amber-800 border-amber-300'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = 'Item Pesanan'
        verbose_name_plural = 'Item Pesanan'

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.price

    @property
    def formatted_subtotal(self):
        try:
            return f"Rp {int(self.subtotal):,}".replace(",", ".")
        except (ValueError, TypeError):
            return f"Rp {self.subtotal}"

    @property
    def formatted_price(self):
        try:
            return f"Rp {int(self.price):,}".replace(",", ".")
        except (ValueError, TypeError):
            return f"Rp {self.price}"
