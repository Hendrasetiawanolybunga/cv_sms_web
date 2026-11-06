from django import forms
from django.contrib.auth.models import User
from .models import Product, CompanyProfile, BankAccount, Customer, Order

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Minimal 6 karakter',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] pr-12 transition'
        }),
        min_length=6,
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ketik ulang password',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] pr-12 transition'
        }),
        min_length=6,
        label='Konfirmasi Password'
    )

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nama lengkap Anda',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Contoh: 081234567890',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'email@example.com',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Alamat pengiriman lengkap...',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if Customer.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Nomor HP sudah terdaftar. Silakan login atau gunakan nomor lain.')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError('Alamat email sudah terdaftar. Silakan login atau gunakan email lain.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Konfirmasi password tidak cocok dengan password yang dimasukkan.')
        return cleaned_data


class CustomerLoginForm(forms.Form):
    identifier = forms.CharField(
        label='Email atau Nomor HP',
        widget=forms.TextInput(attrs={
            'placeholder': 'Masukkan email atau nomor HP',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Masukkan password Anda',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] pr-12 transition'
        })
    )


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['recipient_name', 'recipient_phone', 'shipping_address', 'selected_bank', 'payment_proof']
        widgets = {
            'recipient_name': forms.TextInput(attrs={
                'placeholder': 'Nama lengkap penerima',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'recipient_phone': forms.TextInput(attrs={
                'placeholder': 'Contoh: 081234567890',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'shipping_address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Alamat tujuan pengiriman lengkap beserta kecamatan & kota...',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'selected_bank': forms.RadioSelect(attrs={
                'class': 'text-[#FF807F] focus:ring-[#FF807F]'
            }),
            'payment_proof': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-[#FF807F]/10 file:text-[#FF807F] hover:file:bg-[#FF807F]/20 cursor-pointer'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selected_bank'].queryset = BankAccount.objects.filter(is_active=True)
        self.fields['payment_proof'].required = True


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'unit', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition',
                'placeholder': 'Contoh: Kain Majun Putih Halus'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition',
                'placeholder': '0'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition',
                'placeholder': 'kg, lusin, unit, roll, meter'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition',
                'placeholder': 'Deskripsi detail produk...'
            }),
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-[#FF807F]/10 file:text-[#FF807F] hover:file:bg-[#FF807F]/20 cursor-pointer'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-[#FF807F] focus:ring-[#FF807F] rounded border-slate-300'
            })
        }


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['hero_title', 'hero_subtitle', 'about_text', 'address', 'phone_office', 'phone_whatsapp', 'email', 'hero_image']
        widgets = {
            'hero_title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'hero_subtitle': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'about_text': forms.Textarea(attrs={
                'rows': 5,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'address': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'phone_office': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'phone_whatsapp': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'hero_image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-[#FF807F]/10 file:text-[#FF807F] hover:file:bg-[#FF807F]/20 cursor-pointer'
            })
        }


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_number', 'account_holder', 'is_active']
        widgets = {
            'bank_name': forms.TextInput(attrs={
                'placeholder': 'Contoh: Bank Central Asia (BCA)',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'account_number': forms.TextInput(attrs={
                'placeholder': 'Contoh: 0123456789',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'account_holder': forms.TextInput(attrs={
                'placeholder': 'Contoh: CV. Setia Makmur Surabaya',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-[#FF807F] focus:ring-[#FF807F] rounded border-slate-300'
            })
        }


class StaffUserCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Minimal 6 karakter',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
        }),
        min_length=6
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-[#FF807F] focus:ring-[#FF807F] rounded border-slate-300'
            }),
            'is_superuser': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-[#FF807F] focus:ring-[#FF807F] rounded border-slate-300'
            })
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class StaffUserEditForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Kosongkan jika tidak ingin mengubah password',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
        }),
        label='Password Baru (Opsional)'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#FF807F] transition'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-[#FF807F] focus:ring-[#FF807F] rounded border-slate-300'
            }),
            'is_superuser': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-[#FF807F] focus:ring-[#FF807F] rounded border-slate-300'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-[#FF807F] focus:ring-[#FF807F] rounded border-slate-300'
            })
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        new_pwd = self.cleaned_data.get('new_password')
        if new_pwd:
            user.set_password(new_pwd)
        if commit:
            user.save()
        return user


class CustomerAdminForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Masukkan password (kosongkan jika tidak ingin diubah)',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition'
        }),
        label='Password'
    )

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition',
                'placeholder': 'Nama lengkap pelanggan'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition',
                'placeholder': 'Contoh: 081234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition',
                'placeholder': 'email@example.com'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition',
                'placeholder': 'Alamat pengiriman pelanggan...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-[#8080FF] focus:ring-[#8080FF] rounded border-slate-300'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['password'].required = True
            self.fields['password'].widget.attrs['placeholder'] = 'Minimal 6 karakter'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        qs = Customer.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Nomor HP sudah terdaftar pada pelanggan lain.')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        qs = Customer.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Alamat email sudah terdaftar pada pelanggan lain.')
        return email

    def save(self, commit=True):
        customer = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            customer.set_password(pwd)
        elif not customer.password:
            customer.set_password('customer123')
        if commit:
            customer.save()
        return customer


class AdminOrderCreateForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        required=False,
        label='Akun Pelanggan (Opsional)',
        empty_label='-- Non-Akun / Pelanggan Walk-in --',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition'
        })
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        label='Pilih Produk',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition'
        })
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Kuantitas (Jumlah)',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition'
        })
    )

    class Meta:
        model = Order
        fields = ['recipient_name', 'recipient_phone', 'shipping_address', 'payment_method', 'selected_bank', 'customer']
        widgets = {
            'recipient_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition',
                'placeholder': 'Nama pembeli / walk-in'
            }),
            'recipient_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition',
                'placeholder': '081234567890'
            }),
            'shipping_address': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition',
                'placeholder': 'Alamat pengiriman atau keterangan pengambilan'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition'
            }),
            'selected_bank': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#8080FF] transition'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selected_bank'].required = False
        self.fields['selected_bank'].queryset = BankAccount.objects.filter(is_active=True)
        if not self.initial.get('shipping_address'):
            self.initial['shipping_address'] = 'Ambil Langsung di Tempat (Walk-in Toko)'

