from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from .forms import OrderForm, RegisterForm, SearchForm
from .models import Cart, CartItem, Category, Order, OrderItem, Product, Wishlist


class CategoryModelTest(TestCase):
    """Тесты модели Category"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Электроника',
            slug='elektronika',
            description='Техника и гаджеты'
        )

    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(self.category.name, 'Электроника')
        self.assertEqual(self.category.slug, 'elektronika')

    def test_category_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.category), 'Электроника')

    def test_category_get_absolute_url(self):
        """Тест получения URL категории"""
        url = self.category.get_absolute_url()
        self.assertEqual(url, '/category/elektronika/')


class ProductModelTest(TestCase):
    """Тесты модели Product"""

    def setUp(self):
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            category=self.category,
            name='Смартфон',
            slug='smartphone',
            description='Тестовый смартфон',
            price=Decimal('49990.00'),
            stock=10,
            available=True
        )

    def test_product_creation(self):
        """Тест создания товара"""
        self.assertEqual(self.product.name, 'Смартфон')
        self.assertEqual(self.product.price, Decimal('49990.00'))
        self.assertEqual(self.product.stock, 10)

    def test_product_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.product), 'Смартфон')

    def test_product_get_absolute_url(self):
        """Тест получения URL товара"""
        url = self.product.get_absolute_url()
        self.assertEqual(url, '/product/smartphone/')


class CartModelTest(TestCase):
    """Тесты модели Cart и CartItem"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product1 = Product.objects.create(
            category=self.category, name='Товар 1', slug='tovar-1',
            description='Описание', price=Decimal('1000.00'), stock=10
        )
        self.product2 = Product.objects.create(
            category=self.category, name='Товар 2', slug='tovar-2',
            description='Описание', price=Decimal('2000.00'), stock=5
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        """Тест создания корзины"""
        self.assertEqual(str(self.cart), f'Корзина {self.user.username}')

    def test_cart_empty(self):
        """Тест пустой корзины"""
        self.assertEqual(self.cart.get_total_items(), 0)
        self.assertEqual(self.cart.get_total_price(), 0)

    def test_cart_with_items(self):
        """Тест корзины с товарами"""
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)

        self.assertEqual(self.cart.get_total_items(), 3)
        self.assertEqual(self.cart.get_total_price(), Decimal('4000.00'))

    def test_cart_item_total_price(self):
        """Тест расчёта цены элемента корзины"""
        item = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=3)
        self.assertEqual(item.get_total_price(), Decimal('3000.00'))


class OrderModelTest(TestCase):
    """Тесты модели Order"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            category=self.category, name='Товар', slug='tovar',
            description='Описание', price=Decimal('5000.00'), stock=10
        )
        self.order = Order.objects.create(
            user=self.user,
            first_name='Иван',
            last_name='Иванов',
            email='ivan@test.com',
            phone='+79991234567',
            address='Москва',
            total_price=Decimal('10000.00')
        )

    def test_order_creation(self):
        """Тест создания заказа"""
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.total_price, Decimal('10000.00'))

    def test_order_str(self):
        """Тест строкового представления"""
        self.assertIn(str(self.order.id), str(self.order))

    def test_order_item_creation(self):
        """Тест создания элемента заказа"""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            price=self.product.price,
            quantity=2
        )
        self.assertEqual(item.get_total_price(), Decimal('10000.00'))


class WishlistModelTest(TestCase):
    """Тесты модели Wishlist"""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            category=self.category, name='Товар', slug='tovar',
            description='Описание', price=Decimal('1000.00'), stock=10
        )

    def test_wishlist_creation(self):
        """Тест добавления в избранное"""
        wishlist = Wishlist.objects.create(user=self.user, product=self.product)
        self.assertEqual(str(wishlist), f'{self.user.username} - {self.product.name}')

    def test_wishlist_unique_constraint(self):
        """Тест уникальности записи в избранном"""
        Wishlist.objects.create(user=self.user, product=self.product)
        with self.assertRaises(IntegrityError):
            Wishlist.objects.create(user=self.user, product=self.product)


class RegisterFormTest(TestCase):
    """Тесты формы регистрации"""

    def test_valid_form(self):
        """Тест валидной формы"""
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """Тест несовпадения паролей"""
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'password1': 'complexpass123',
            'password2': 'differentpass'
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())


class OrderFormTest(TestCase):
    """Тесты формы заказа"""

    def test_valid_form(self):
        """Тест валидной формы"""
        data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@test.com',
            'phone': '+79991234567',
            'address': 'г. Москва, ул. Тестовая, д. 1',
            'note': ''
        }
        form = OrderForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_phone(self):
        """Тест невалидного телефона"""
        data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@test.com',
            'phone': 'invalid',
            'address': 'Москва',
            'note': ''
        }
        form = OrderForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)


class SearchFormTest(TestCase):
    """Тесты формы поиска"""

    def test_empty_search(self):
        """Тест пустого поиска"""
        form = SearchForm(data={'q': ''})
        self.assertTrue(form.is_valid())

    def test_search_with_query(self):
        """Тест поиска с запросом"""
        form = SearchForm(data={'q': 'смартфон'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['q'], 'смартфон')


class HomeViewTest(TestCase):
    """Тесты главной страницы"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            category=self.category, name='Товар', slug='tovar',
            description='Описание', price=Decimal('1000.00'), stock=10, available=True
        )

    def test_home_page_status(self):
        """Тест статуса главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        """Тест шаблона главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'shop/home.html')

    def test_home_page_content(self):
        """Тест контента главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'ShopMarket')


class ProductViewTest(TestCase):
    """Тесты страниц товаров"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Электроника', slug='elektronika')
        self.product = Product.objects.create(
            category=self.category, name='Смартфон', slug='smartphone',
            description='Описание смартфона', price=Decimal('50000.00'), stock=5, available=True
        )

    def test_product_list_view(self):
        """Тест списка товаров"""
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Смартфон')

    def test_product_detail_view(self):
        """Тест детальной страницы товара"""
        response = self.client.get(reverse('product_detail', kwargs={'slug': 'smartphone'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Смартфон')
        self.assertContains(response, '50000')

    def test_category_detail_view(self):
        """Тест страницы категории"""
        response = self.client.get(reverse('category_detail', kwargs={'slug': 'elektronika'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Электроника')


class SearchViewTest(TestCase):
    """Тесты поиска"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Тест', slug='test')
        Product.objects.create(
            category=self.category, name='Python книга', slug='python-book',
            description='Изучаем Python', price=Decimal('1000.00'), stock=10, available=True
        )
        Product.objects.create(
            category=self.category, name='Java книга', slug='java-book',
            description='Изучаем Java', price=Decimal('1200.00'), stock=5, available=True
        )

    def test_search_results(self):
        """Тест результатов поиска"""
        response = self.client.get(reverse('search'), {'q': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python книга')
        self.assertNotContains(response, 'Java книга')

    def test_empty_search(self):
        """Тест пустого поиска"""
        response = self.client.get(reverse('search'), {'q': ''})
        self.assertEqual(response.status_code, 200)


class AuthViewTest(TestCase):
    """Тесты аутентификации"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        Cart.objects.create(user=self.user)

    def test_login_page(self):
        """Тест страницы входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """Тест успешного входа"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):
        """Тест неверного входа"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_register_page(self):
        """Тест страницы регистрации"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """Тест выхода"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class CartViewTest(TestCase):
    """Тесты корзины"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.cart = Cart.objects.create(user=self.user)
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            category=self.category, name='Товар', slug='tovar',
            description='Описание', price=Decimal('1000.00'), stock=10, available=True
        )

    def test_cart_requires_login(self):
        """Тест требования авторизации для корзины"""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_cart_view_authenticated(self):
        """Тест просмотра корзины авторизованным пользователем"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        """Тест добавления товара в корзину"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('add_to_cart', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cart.items.count(), 1)

    def test_add_to_cart_increases_quantity(self):
        """Тест увеличения количества при повторном добавлении"""
        self.client.login(username='testuser', password='password123')
        self.client.post(reverse('add_to_cart', kwargs={'product_id': self.product.id}))
        self.client.post(reverse('add_to_cart', kwargs={'product_id': self.product.id}))
        item = self.cart.items.first()
        self.assertEqual(item.quantity, 2)

    def test_remove_from_cart(self):
        """Тест удаления товара из корзины"""
        self.client.login(username='testuser', password='password123')
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        response = self.client.post(reverse('remove_from_cart', kwargs={'item_id': item.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cart.items.count(), 0)

    def test_update_cart_item(self):
        """Тест обновления количества товара"""
        self.client.login(username='testuser', password='password123')
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.client.post(
            reverse('update_cart_item', kwargs={'item_id': item.id}),
            {'quantity': 5}
        )
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)


class CheckoutViewTest(TestCase):
    """Тесты оформления заказа"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.cart = Cart.objects.create(user=self.user)
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            category=self.category, name='Товар', slug='tovar',
            description='Описание', price=Decimal('1000.00'), stock=10, available=True
        )

    def test_checkout_requires_login(self):
        """Тест требования авторизации для оформления"""
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_empty_cart_redirect(self):
        """Тест редиректа при пустой корзине"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('cart', response.url)

    def test_checkout_with_items(self):
        """Тест страницы оформления с товарами"""
        self.client.login(username='testuser', password='password123')
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_success(self):
        """Тест успешного оформления заказа"""
        self.client.login(username='testuser', password='password123')
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        response = self.client.post(reverse('checkout'), {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@test.com',
            'phone': '+79991234567',
            'address': 'г. Москва',
            'note': ''
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, Decimal('2000.00'))

        # Проверяем что stock уменьшился
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        # Проверяем что корзина очищена
        self.assertEqual(self.cart.items.count(), 0)

    def test_checkout_insufficient_stock(self):
        """Тест оформления при недостатке товара"""
        self.client.login(username='testuser', password='password123')
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=100)

        response = self.client.post(reverse('checkout'), {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@test.com',
            'phone': '+79991234567',
            'address': 'г. Москва',
            'note': ''
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn('cart', response.url)
        self.assertEqual(Order.objects.count(), 0)


class WishlistViewTest(TestCase):
    """Тесты избранного"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.category = Category.objects.create(name='Тест', slug='test')
        self.product = Product.objects.create(
            category=self.category, name='Товар', slug='tovar',
            description='Описание', price=Decimal('1000.00'), stock=10, available=True
        )

    def test_wishlist_requires_login(self):
        """Тест требования авторизации для избранного"""
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 302)

    def test_wishlist_view(self):
        """Тест просмотра избранного"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 200)

    def test_toggle_wishlist_add(self):
        """Тест добавления в избранное"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('toggle_wishlist', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Wishlist.objects.filter(user=self.user, product=self.product).exists())

    def test_toggle_wishlist_remove(self):
        """Тест удаления из избранного"""
        self.client.login(username='testuser', password='password123')
        Wishlist.objects.create(user=self.user, product=self.product)
        response = self.client.post(reverse('toggle_wishlist', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Wishlist.objects.filter(user=self.user, product=self.product).exists())


class OrderViewTest(TestCase):
    """Тесты заказов"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.order = Order.objects.create(
            user=self.user,
            first_name='Иван',
            last_name='Иванов',
            email='ivan@test.com',
            phone='+79991234567',
            address='Москва',
            total_price=Decimal('5000.00')
        )

    def test_order_list_requires_login(self):
        """Тест требования авторизации для списка заказов"""
        response = self.client.get(reverse('order_list'))
        self.assertEqual(response.status_code, 302)

    def test_order_list_view(self):
        """Тест списка заказов"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('order_list'))
        self.assertEqual(response.status_code, 200)

    def test_order_detail_view(self):
        """Тест детальной страницы заказа"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('order_detail', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 200)

    def test_order_detail_other_user(self):
        """Тест просмотра чужого заказа"""
        User.objects.create_user('other', 'other@test.com', 'password123')
        self.client.login(username='other', password='password123')
        response = self.client.get(reverse('order_detail', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 404)


class ProfileViewTest(TestCase):
    """Тесты профиля"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')

    def test_profile_requires_login(self):
        """Тест требования авторизации для профиля"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_view(self):
        """Тест страницы профиля"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
