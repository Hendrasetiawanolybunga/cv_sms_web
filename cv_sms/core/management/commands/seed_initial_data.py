from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import CompanyProfile, BankAccount, Product, Customer

class Command(BaseCommand):
    help = 'Mengisi data awal untuk CV. Setia Makmur Surabaya'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('=== Mulai seeding data awal CV. Setia Makmur Surabaya ==='))

        # 1. Superuser / Admin Internal
        admin_username = 'admin'
        admin_email = 'admin@setiamakmur.com'
        admin_pass = 'admin123'
        user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': admin_email,
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Administrator',
                'last_name': 'Setia Makmur',
            }
        )
        if created:
            user.set_password(admin_pass)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'[OK] Admin dibuat: username="{admin_username}", password="{admin_pass}"'))
        else:
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'[OK] Admin sudah ada: username="{admin_username}"'))

        # 2. Company Profile
        profile, created = CompanyProfile.objects.get_or_create(
            id=1,
            defaults={
                'hero_title': 'CV. Setia Makmur Surabaya',
                'hero_subtitle': 'Mitra Solusi Kebutuhan Industri, Konveksi & Permesinan Terpercaya di Surabaya.',
                'about_text': (
                    'CV. Setia Makmur Surabaya adalah perusahaan yang berdedikasi menyediakan berbagai kebutuhan '
                    'perlengkapan industri, pabrik, bengkel, dan konveksi. Berlokasi strategis di Surabaya, kami menyediakan '
                    'kain majun berkualitas dengan daya serap tinggi, sarung tangan pelindung kerja, tali rafia super kuat, '
                    'masker higienis, serta aneka mesin produksi dan mesin penggulung berstandar industri. '
                    'Dengan komitmen menjaga mutu, ketersediaan stok, dan pelayanan cepat, kami siap menjadi mitra bisnis jangka panjang Anda.'
                ),
                'address': 'Jln. Wisma Kedung Asem Indah J-30 Surabaya',
                'opening_hours': 'Senin - Sabtu: 08.00 - 17.00 WIB',
                'phone_office': '031-8793055',
                'phone_whatsapp': '081-330780729 / 082-232377866',
                'phone_whatsapp_1': '081-330780729',
                'phone_whatsapp_2': '082-232377866',
                'email': 'setia.makmur60@yahoo.com',
            }
        )
        if not created:
            profile.hero_title = 'CV. Setia Makmur Surabaya'
            profile.hero_subtitle = 'Mitra Solusi Kebutuhan Industri, Konveksi & Permesinan Terpercaya di Surabaya.'
            profile.about_text = (
                'CV. Setia Makmur Surabaya adalah perusahaan yang berdedikasi menyediakan berbagai kebutuhan '
                'perlengkapan industri, pabrik, bengkel, dan konveksi. Berlokasi strategis di Surabaya, kami menyediakan '
                'kain majun berkualitas dengan daya serap tinggi, sarung tangan pelindung kerja, tali rafia super kuat, '
                'masker higienis, serta aneka mesin produksi dan mesin penggulung berstandar industri. '
                'Dengan komitmen menjaga mutu, ketersediaan stok, dan pelayanan cepat, kami siap menjadi mitra bisnis jangka panjang Anda.'
            )
            profile.address = 'Jln. Wisma Kedung Asem Indah J-30 Surabaya'
            profile.opening_hours = 'Senin - Sabtu: 08.00 - 17.00 WIB'
            profile.phone_office = '031-8793055'
            profile.phone_whatsapp = '081-330780729 / 082-232377866'
            profile.phone_whatsapp_1 = '081-330780729'
            profile.phone_whatsapp_2 = '082-232377866'
            profile.email = 'setia.makmur60@yahoo.com'
            profile.save()
            self.stdout.write(self.style.SUCCESS('[OK] Profil Perusahaan diperbarui'))
        else:
            self.stdout.write(self.style.SUCCESS('[OK] Profil Perusahaan dibuat'))

        # 3. 6 Produk Awal (Katalog B2B Pabrik)
        initial_products = [
            {
                'name': 'Kain Majun',
                'price': Decimal('5500.00'),
                'unit': 'kg',
                'min_order': 50,
                'step_order': 10,
                'description': 'Kain majun katun bersih, daya serap tinggi untuk lap oli, mesin pabrik, dan bengkel industri.',
                'is_active': True,
            },
            {
                'name': 'Sarung Tangan',
                'price': Decimal('18000.00'),
                'unit': 'lusin',
                'min_order': 10,
                'step_order': 1,
                'description': 'Sarung tangan rajut kerja tebal dan lentur untuk melindungi tangan di area gudang dan produksi.',
                'is_active': True,
            },
            {
                'name': 'Tali Rafia',
                'price': Decimal('14000.00'),
                'unit': 'kg',
                'min_order': 250,
                'step_order': 25,
                'description': 'Tali rafia super alot, tahan tarikan kencang, ideal untuk pengemasan kargo dan barang industri.',
                'is_active': True,
            },
            {
                'name': 'Mesin Produksi',
                'price': Decimal('90000000.00'),
                'unit': 'unit',
                'min_order': 1,
                'step_order': 1,
                'description': 'Mesin industri performa tinggi untuk lini manufaktur dengan efisiensi daya dan durabilitas tinggi.',
                'is_active': True,
            },
            {
                'name': 'Mesin Gulung',
                'price': Decimal('6500000.00'),
                'unit': 'unit',
                'min_order': 1,
                'step_order': 1,
                'description': 'Mesin penggulung tali dan kain berkecepatan presisi, mudah diatur dan minim perawatan.',
                'is_active': True,
            },
            {
                'name': 'Masker',
                'price': Decimal('6000.00'),
                'unit': 'lusin',
                'min_order': 100,
                'step_order': 10,
                'description': 'Masker pelindung debu dan partikel halus, nyaman digunakan untuk pekerja konveksi dan pabrik.',
                'is_active': True,
            },
        ]

        for p_data in initial_products:
            prod, p_created = Product.objects.get_or_create(
                name=p_data['name'],
                defaults=p_data
            )
            if not p_created:
                prod.price = p_data['price']
                prod.unit = p_data['unit']
                prod.min_order = p_data['min_order']
                prod.step_order = p_data['step_order']
                prod.description = p_data['description']
                prod.is_active = True
                prod.save()
            self.stdout.write(self.style.SUCCESS(f'[OK] Produk: {prod.name} ({prod.formatted_price}/{prod.unit}, Min. Order: {prod.min_order})'))

        # 4. Bank Accounts
        banks = [
            {
                'bank_name': 'Bank Central Asia (BCA)',
                'account_number': '0123456789',
                'account_holder': 'CV Setia Makmur Surabaya',
                'is_active': True,
            },
            {
                'bank_name': 'Bank Mandiri',
                'account_number': '1410098765432',
                'account_holder': 'CV Setia Makmur Surabaya',
                'is_active': True,
            },
            {
                'bank_name': 'Bank Rakyat Indonesia (BRI)',
                'account_number': '001201009988501',
                'account_holder': 'CV Setia Makmur Surabaya',
                'is_active': True,
            },
        ]

        for b_data in banks:
            bank, b_created = BankAccount.objects.get_or_create(
                account_number=b_data['account_number'],
                defaults=b_data
            )
            if not b_created:
                bank.bank_name = b_data['bank_name']
                bank.account_holder = b_data['account_holder']
                bank.is_active = True
                bank.save()
            self.stdout.write(self.style.SUCCESS(f'[OK] Rekening: {bank.bank_name} - {bank.account_number}'))

        # 5. Dummy Customer for testing
        test_customer, c_created = Customer.objects.get_or_create(
            email='budi@example.com',
            defaults={
                'name': 'Budi Santoso',
                'phone': '081234567890',
                'address': 'Jl. Rungkut Industri No. 12, Surabaya',
                'is_active': True,
            }
        )
        if c_created:
            test_customer.set_password('customer123')
            test_customer.save()
            self.stdout.write(self.style.SUCCESS('[OK] Sample Customer: budi@example.com / customer123'))

        self.stdout.write(self.style.SUCCESS('=== Seeding data awal berhasil selesai! ==='))

