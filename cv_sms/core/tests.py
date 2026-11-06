from decimal import Decimal
import io
from PIL import Image

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import CompanyProfile, BankAccount, Product, ProductImage


def create_dummy_image():
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), color=(255, 128, 127))
    image.save(file, 'jpeg')
    file.seek(0)
    return SimpleUploadedFile('test_image.jpg', file.read(), content_type='image/jpeg')


class B2BFactoryCatalogTestCase(TestCase):
    def setUp(self):
        # Admin / Staff user
        self.staff_user = User.objects.create_user(
            username='staffadmin',
            email='staff@setiamakmur.com',
            password='password123',
            is_staff=True
        )

        # Company profile
        self.profile = CompanyProfile.objects.create(
            hero_title='CV. Setia Makmur Surabaya',
            hero_subtitle='Penyedia Kain Majun & Mesin Industri Berkualitas',
            about_text='Produsen dan distributor perlengkapan industri terpercaya di Surabaya.',
            address='Jln. Wisma Kedung Asem Indah J-30 Surabaya',
            opening_hours='Senin - Sabtu: 08.00 - 17.00 WIB',
            phone_office='031-8793055',
            phone_whatsapp_1='081-330780729',
            phone_whatsapp_2='082-232377866',
            phone_whatsapp='081-330780729 / 082-232377866',
            email='setia.makmur60@yahoo.com'
        )

        # Bank accounts
        self.bank = BankAccount.objects.create(
            bank_name='Bank Central Asia (BCA)',
            account_number='0123456789',
            account_holder='CV Setia Makmur Surabaya',
            is_active=True
        )

        # Products with B2B attributes
        self.product_majun = Product.objects.create(
            name='Kain Majun Putih Katun',
            price=Decimal('5500.00'),
            unit='kg',
            min_order=50,
            step_order=10,
            description='Kain majun katun bersih tanpa kotoran.',
            is_active=True
        )
        self.product_gloves = Product.objects.create(
            name='Sarung Tangan Kerja Rajut',
            price=Decimal('18000.00'),
            unit='lusin',
            min_order=10,
            step_order=1,
            description='Sarung tangan kerja rajut tebal 7 benang.',
            is_active=True
        )
        self.product_machine = Product.objects.create(
            name='Mesin Produksi & Gulung Otomatis',
            price=Decimal('15000000.00'),
            unit='unit',
            min_order=1,
            step_order=1,
            description='Mesin penggulung tali dan kain berkecepatan tinggi.',
            is_active=True
        )

    def test_company_profile_properties(self):
        """Test CompanyProfile clean_whatsapp, wa_url_1, wa_url_2 and custom fields."""
        self.assertEqual(self.profile.wa_url_1, '6281330780729')
        self.assertEqual(self.profile.wa_url_2, '6282232377866')
        self.assertEqual(self.profile.clean_whatsapp, '6281330780729')
        self.assertEqual(self.profile.opening_hours, 'Senin - Sabtu: 08.00 - 17.00 WIB')

    def test_b2b_product_attributes(self):
        """Test Product min_order, step_order, formatted_price, and slug generation."""
        self.assertEqual(self.product_majun.min_order, 50)
        self.assertEqual(self.product_majun.step_order, 10)
        self.assertEqual(self.product_majun.formatted_price, 'Rp 5.500')
        self.assertEqual(self.product_majun.slug, 'kain-majun-putih-katun')

    def test_public_home_portal_rendering(self):
        """Public home view renders schema.org, product cards, min order badges, and WA buttons."""
        client = Client()
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        # SEO Schema.org check
        self.assertContains(response, 'schema.org')
        self.assertContains(response, '"@type": "Factory"')
        self.assertContains(response, '08.00 - 17.00 WIB')

        # Catalog products check
        self.assertContains(response, 'Kain Majun Putih Katun')
        self.assertContains(response, 'Sarung Tangan Kerja Rajut')
        self.assertContains(response, 'Min. Order: 50 kg')
        self.assertContains(response, 'Min. Order: 10 lusin')
        self.assertContains(response, 'Pesan WA 1')
        self.assertContains(response, 'WA 2')
        self.assertContains(response, '6281330780729')
        self.assertContains(response, '6282232377866')
        self.assertContains(response, 'Lihat Foto POV')
        self.assertContains(response, 'id="product-gallery-modal"')

        # Banks in footer check
        self.assertContains(response, 'Bank Central Asia (BCA)')
        self.assertContains(response, '0123456789')

    def test_multi_image_pov_gallery(self):
        """Test gallery model, all_images property, dashboard upload and delete endpoint."""
        client = Client()
        client.login(username='staffadmin', password='password123')

        # 1. Test all_images property with cover and gallery images
        self.product_majun.image = create_dummy_image()
        self.product_majun.save()

        g_img1 = ProductImage.objects.create(
            product=self.product_majun,
            image=create_dummy_image(),
            caption='Tampak Serat',
            order=0
        )
        g_img2 = ProductImage.objects.create(
            product=self.product_majun,
            image=create_dummy_image(),
            caption='Kemasan Karung 50kg',
            order=1
        )

        all_imgs = self.product_majun.all_images
        self.assertEqual(len(all_imgs), 3) # 1 cover + 2 gallery
        self.assertTrue(all_imgs[0]['is_cover'])
        self.assertFalse(all_imgs[1]['is_cover'])

        # 2. Test AJAX delete endpoint
        del_ajax = client.post(
            reverse('dashboard_product_image_delete', args=[g_img1.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(del_ajax.status_code, 200)
        self.assertEqual(del_ajax.json().get('status'), 'success')
        self.assertFalse(ProductImage.objects.filter(id=g_img1.id).exists())

        # 3. Test standard POST delete endpoint
        del_post = client.post(reverse('dashboard_product_image_delete', args=[g_img2.id]), follow=True)
        self.assertEqual(del_post.status_code, 200)
        self.assertFalse(ProductImage.objects.filter(id=g_img2.id).exists())

    def test_dashboard_access_control(self):
        """Dashboard requires staff user; anonymous users are redirected to login."""
        client = Client()
        # Anonymous
        resp = client.get(reverse('dashboard_index'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/login/', resp.url)

        # Staff user login
        client.login(username='staffadmin', password='password123')
        staff_resp = client.get(reverse('dashboard_index'))
        self.assertEqual(staff_resp.status_code, 200)
        self.assertContains(staff_resp, 'staffadmin')
        self.assertContains(staff_resp, 'Produk Aktif')

    def test_dashboard_product_crud_with_b2b_fields(self):
        """Staff creates, edits, toggles, and deletes products with min_order and step_order."""
        client = Client()
        client.login(username='staffadmin', password='password123')

        # Create Product
        create_resp = client.post(reverse('dashboard_product_create'), {
            'name': 'Tali Rafia Roll Besar',
            'price': '14500',
            'unit': 'kg',
            'min_order': 250,
            'step_order': 25,
            'description': 'Tali rafia warna hitam super ulet.',
            'is_active': True
        }, follow=True)
        self.assertEqual(create_resp.status_code, 200)
        self.assertTrue(Product.objects.filter(name='Tali Rafia Roll Besar').exists())

        new_prod = Product.objects.get(name='Tali Rafia Roll Besar')
        self.assertEqual(new_prod.slug, 'tali-rafia-roll-besar')
        self.assertEqual(new_prod.min_order, 250)
        self.assertEqual(new_prod.step_order, 25)

        # Edit Product
        edit_resp = client.post(reverse('dashboard_product_edit', args=[new_prod.id]), {
            'name': 'Tali Rafia Roll Besar Premium',
            'price': '15000',
            'unit': 'kg',
            'min_order': 300,
            'step_order': 50,
            'description': 'Tali rafia kualitas ekspor.',
            'is_active': True
        }, follow=True)
        self.assertEqual(edit_resp.status_code, 200)
        new_prod.refresh_from_db()
        self.assertEqual(new_prod.name, 'Tali Rafia Roll Besar Premium')
        self.assertEqual(new_prod.min_order, 300)
        self.assertEqual(new_prod.step_order, 50)

        # Toggle Product Status
        client.get(reverse('dashboard_product_toggle', args=[new_prod.id]))
        new_prod.refresh_from_db()
        self.assertFalse(new_prod.is_active)

        # Delete Product
        del_resp = client.post(reverse('dashboard_product_delete', args=[new_prod.id]), follow=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertFalse(Product.objects.filter(id=new_prod.id).exists())

    def test_dashboard_company_profile_settings(self):
        """Staff updates company profile including operating hours."""
        client = Client()
        client.login(username='staffadmin', password='password123')

        settings_resp = client.post(reverse('dashboard_settings_company_profile'), {
            'hero_title': 'CV. Setia Makmur Surabaya - B2B Supplier',
            'hero_subtitle': 'Pabrik & Distributor Terlengkap di Surabaya',
            'about_text': 'Mendukung pengadaan pabrik di Jawa Timur sejak bertahun-tahun.',
            'address': 'Jln. Wisma Kedung Asem Indah J-30 Surabaya, Jawa Timur',
            'opening_hours': 'Senin - Jumat: 08.00 - 17.00 WIB, Sabtu: 08.00 - 14.00 WIB',
            'phone_office': '031-8793055',
            'phone_whatsapp_1': '081-330780729',
            'phone_whatsapp_2': '082-232377866',
            'email': 'admin@setiamakmur.com'
        }, follow=True)
        self.assertEqual(settings_resp.status_code, 200)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.hero_title, 'CV. Setia Makmur Surabaya - B2B Supplier')
        self.assertEqual(self.profile.wa_url_1, '6281330780729')
        self.assertEqual(self.profile.wa_url_2, '6282232377866')
        self.assertIn('Sabtu: 08.00 - 14.00 WIB', self.profile.opening_hours)

    def test_dashboard_users_management(self):
        """Staff can view the staff users list."""
        client = Client()
        client.login(username='staffadmin', password='password123')

        resp = client.get(reverse('dashboard_user_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'staffadmin')
        self.assertContains(resp, 'staff@setiamakmur.com')
