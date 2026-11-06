from decimal import Decimal
import io
from PIL import Image

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import CompanyProfile, BankAccount, Product, Customer, Order, OrderItem
from core.cart import Cart


def create_dummy_image():
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), color=(255, 128, 127))
    image.save(file, 'jpeg')
    file.seek(0)
    return SimpleUploadedFile('test_proof.jpg', file.read(), content_type='image/jpeg')


class DualAuthAndModelsTestCase(TestCase):
    def setUp(self):
        # Admin / Staff user
        self.staff_user = User.objects.create_user(
            username='staffadmin',
            email='staff@setiamakmur.com',
            password='password123',
            is_staff=True
        )

        # Customer user
        self.customer = Customer.objects.create(
            name='Ahmad Fauzi',
            phone='081299998888',
            email='ahmad@example.com',
            address='Jl. Rungkut Asri Timur No. 45, Surabaya'
        )
        self.customer.set_password('customerpass123')
        self.customer.save()

        # Company profile
        self.profile = CompanyProfile.objects.create(
            hero_title='CV. Setia Makmur Surabaya',
            hero_subtitle='Penyedia Kain Majun & Mesin Industri',
            address='Jln. Wisma Kedung Asem Indah J-30 Surabaya',
            phone_office='031-8793055',
            phone_whatsapp='081-330780729',
            email='setia.makmur60@yahoo.com'
        )

        # Bank
        self.bank = BankAccount.objects.create(
            bank_name='Bank Central Asia (BCA)',
            account_number='0123456789',
            account_holder='CV Setia Makmur Surabaya',
            is_active=True
        )

        # Products
        self.product1 = Product.objects.create(
            name='Kain Majun Putih',
            price=Decimal('5500.00'),
            unit='kg',
            description='Kain majun katun bersih',
            is_active=True
        )
        self.product2 = Product.objects.create(
            name='Sarung Tangan Rajut',
            price=Decimal('18000.00'),
            unit='lusin',
            description='Sarung tangan kerja rajut tebal',
            is_active=True
        )

    def test_customer_independent_hashing(self):
        """Customer model hashes with make_password and checks with check_password."""
        self.assertTrue(self.customer.check_password('customerpass123'))
        self.assertFalse(self.customer.check_password('wrongpass'))
        # Customer must NOT be in internal User table
        self.assertFalse(User.objects.filter(username=self.customer.email).exists())
        self.assertFalse(User.objects.filter(email=self.customer.email).exists())

    def test_customer_login_session(self):
        """Customer login stores customer_id in session."""
        client = Client()
        response = client.post(reverse('customer_login'), {
            'identifier': 'ahmad@example.com',
            'password': 'customerpass123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.session.get('customer_id'), self.customer.id)

        # Test customer logout
        logout_resp = client.get(reverse('customer_logout'), follow=True)
        self.assertIsNone(client.session.get('customer_id'))

    def test_dashboard_access_control(self):
        """Dashboard requires staff user, anonymous and non-staff are redirected."""
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

    def test_cart_operations(self):
        """Test cart session-based addition, update, total price calculation."""
        client = Client()
        # Add product1 (qty 2)
        client.post(reverse('cart_add', args=[self.product1.id]), {'quantity': 2})
        # Add product2 (qty 1)
        client.post(reverse('cart_add', args=[self.product2.id]), {'quantity': 1})

        cart_resp = client.get(reverse('cart_detail'))
        self.assertEqual(cart_resp.status_code, 200)
        self.assertContains(cart_resp, 'Kain Majun Putih')
        self.assertContains(cart_resp, 'Sarung Tangan Rajut')

        # Total should be (2 * 5500) + (1 * 18000) = 11000 + 18000 = 29000
        cart = Cart(cart_resp.wsgi_request)
        self.assertEqual(cart.get_total_price(), Decimal('29000.00'))

    def test_multi_product_checkout_flow(self):
        """Test multi-product checkout, bank selection, payment proof upload, Order creation."""
        client = Client()
        # Customer login
        client.post(reverse('customer_login'), {
            'identifier': '081299998888',
            'password': 'customerpass123'
        })

        # Add 2 products to cart
        client.post(reverse('cart_add', args=[self.product1.id]), {'quantity': 3}) # 3 * 5500 = 16500
        client.post(reverse('cart_add', args=[self.product2.id]), {'quantity': 2}) # 2 * 18000 = 36000
        # Grand total = 52500

        dummy_img = create_dummy_image()
        checkout_resp = client.post(reverse('checkout'), {
            'recipient_name': 'Pak Budi Gudang',
            'recipient_phone': '081234567890',
            'shipping_address': 'Kawasan Industri Rungkut Blok B-5 Surabaya',
            'selected_bank': self.bank.id,
            'payment_proof': dummy_img,
        }, follow=True)

        self.assertEqual(checkout_resp.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()
        self.assertTrue(order.order_code.startswith('SMS-'))
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.total_amount, Decimal('52500.00'))
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.items.count(), 2)

        # Cart should now be empty
        self.assertEqual(len(client.session.get('cart', {})), 0)

        # Test Order Detail page
        order_resp = client.get(reverse('order_detail', args=[order.order_code]))
        self.assertEqual(order_resp.status_code, 200)
        self.assertContains(order_resp, order.order_code)
        self.assertContains(order_resp, 'Pak Budi Gudang')

    def test_dashboard_order_review_and_status_update(self):
        """Staff reviews payment proof in dashboard and changes status to confirmed."""
        order = Order.objects.create(
            order_code='SMS-20261106-TEST',
            customer=self.customer,
            recipient_name='Pak Budi',
            recipient_phone='081234567890',
            shipping_address='Surabaya',
            total_amount=Decimal('52500.00'),
            selected_bank=self.bank,
            payment_proof=create_dummy_image(),
            status='pending'
        )

        client = Client()
        client.login(username='staffadmin', password='password123')

        # Detail review
        detail_resp = client.get(reverse('dashboard_order_detail', args=[order.id]))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, 'SMS-20261106-TEST')

        # Update status to confirmed
        status_resp = client.post(reverse('dashboard_order_status_update', args=[order.id]), {
            'status': 'confirmed'
        }, follow=True)
        self.assertEqual(status_resp.status_code, 200)

        order.refresh_from_db()
        self.assertEqual(order.status, 'confirmed')

    def test_product_crud_dashboard(self):
        """Staff creates, edits, toggles, and deletes product."""
        client = Client()
        client.login(username='staffadmin', password='password123')

        # Create
        create_resp = client.post(reverse('dashboard_product_create'), {
            'name': 'Tali Rafia Merah',
            'price': '14000',
            'unit': 'kg',
            'description': 'Tali rafia super kuat',
            'is_active': True
        }, follow=True)
        self.assertEqual(create_resp.status_code, 200)
        self.assertTrue(Product.objects.filter(name='Tali Rafia Merah').exists())

        new_prod = Product.objects.get(name='Tali Rafia Merah')
        self.assertEqual(new_prod.slug, 'tali-rafia-merah')

        # Toggle
        client.get(reverse('dashboard_product_toggle', args=[new_prod.id]))
        new_prod.refresh_from_db()
        self.assertFalse(new_prod.is_active)

    def test_checkout_requires_login(self):
        """Anonymous user must be redirected to login when accessing checkout."""
        client = Client()
        # Add item to cart first
        client.post(reverse('cart_add', args=[self.product1.id]), {'quantity': 1})
        resp = client.get(reverse('checkout'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('customer_login'), resp.url)

    def test_order_detail_requires_customer_ownership(self):
        """Customer cannot view another customer's order."""
        other_customer = Customer.objects.create(
            name='Dewi Lestari',
            phone='087711112222',
            email='dewi@example.com'
        )
        other_customer.set_password('pass123')
        other_customer.save()

        order = Order.objects.create(
            order_code='SMS-20261106-OTHER',
            customer=other_customer,
            recipient_name='Dewi',
            recipient_phone='087711112222',
            shipping_address='Surabaya',
            total_amount=Decimal('10000.00'),
            selected_bank=self.bank,
            payment_proof=create_dummy_image(),
            status='pending'
        )

        client = Client()
        # Login as self.customer (Ahmad Fauzi)
        client.post(reverse('customer_login'), {
            'identifier': '081299998888',
            'password': 'customerpass123'
        })

        resp = client.get(reverse('order_detail', args=[order.order_code]), follow=True)
        self.assertEqual(resp.status_code, 200)
        # Should be redirected to customer_orders
        self.assertContains(resp, 'Riwayat Pesanan Saya')

    def test_dashboard_customer_crud(self):
        """Staff can create, edit, and delete customers from dashboard."""
        client = Client()
        client.login(username='staffadmin', password='password123')

        # Create
        create_resp = client.post(reverse('dashboard_customer_create'), {
            'name': 'Pelanggan Baru',
            'phone': '081333444555',
            'email': 'pelanggan.baru@example.com',
            'password': 'newpassword123',
            'address': 'Jl. Kenjeran No. 88, Surabaya',
            'is_active': True
        }, follow=True)
        self.assertEqual(create_resp.status_code, 200)
        self.assertTrue(Customer.objects.filter(phone='081333444555').exists())

        new_cust = Customer.objects.get(phone='081333444555')
        self.assertTrue(new_cust.check_password('newpassword123'))

        # Edit
        edit_resp = client.post(reverse('dashboard_customer_edit', args=[new_cust.id]), {
            'name': 'Pelanggan Baru Edit',
            'phone': '081333444555',
            'email': 'pelanggan.baru@example.com',
            'address': 'Jl. Kenjeran No. 89, Surabaya',
            'is_active': True
        }, follow=True)
        self.assertEqual(edit_resp.status_code, 200)
        new_cust.refresh_from_db()
        self.assertEqual(new_cust.name, 'Pelanggan Baru Edit')

        # Delete
        del_resp = client.post(reverse('dashboard_customer_delete', args=[new_cust.id]), follow=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertFalse(Customer.objects.filter(id=new_cust.id).exists())

    def test_dashboard_walkin_order_create_and_delete(self):
        """Staff can record a walk-in cash transaction without payment proof and delete it."""
        client = Client()
        client.login(username='staffadmin', password='password123')

        # Create Walk-in order with 2 items
        create_resp = client.post(reverse('dashboard_order_create'), {
            'recipient_name': 'Pembeli Tunai Toko',
            'recipient_phone': '085566778899',
            'shipping_address': 'Ambil Langsung di Toko',
            'payment_method': 'cash_walkin',
            'product_ids[]': [self.product1.id, self.product2.id],
            'quantities[]': [4, 1], # (4 * 5500) + (1 * 18000) = 22000 + 18000 = 40000
            'product': self.product1.id,
            'quantity': 1,
        }, follow=True)

        self.assertEqual(create_resp.status_code, 200)
        walkin_order = Order.objects.filter(recipient_name='Pembeli Tunai Toko').first()
        self.assertIsNotNone(walkin_order)
        self.assertEqual(walkin_order.status, 'confirmed')
        self.assertEqual(walkin_order.payment_method, 'cash_walkin')
        self.assertEqual(walkin_order.total_amount, Decimal('40000.00'))
        self.assertEqual(walkin_order.items.count(), 2)

        # Delete Order
        del_resp = client.post(reverse('dashboard_order_delete', args=[walkin_order.id]), follow=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertFalse(Order.objects.filter(id=walkin_order.id).exists())
