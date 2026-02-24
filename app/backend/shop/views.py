from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Category, Product, Cart, CartItem, Order, OrderItem, Wishlist
from .forms import RegisterForm, LoginForm, OrderForm, SearchForm


def home(request):
    """Главная страница"""
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(available=True)[:8]
    return render(request, 'shop/home.html', {
        'categories': categories,
        'featured_products': featured_products,
    })


def product_list(request):
    """Список всех товаров"""
    products = Product.objects.filter(available=True)
    search_form = SearchForm(request.GET)

    if search_form.is_valid():
        query = search_form.cleaned_data.get('q')
        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

    return render(request, 'shop/product_list.html', {
        'products': products,
        'search_form': search_form,
    })


def product_detail(request, slug):
    """Детальная страница товара"""
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    })


def category_detail(request, slug):
    """Страница категории"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    return render(request, 'shop/category_detail.html', {
        'category': category,
        'products': products,
    })


def search(request):
    """Поиск товаров"""
    query = request.GET.get('q', '')
    products = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            available=True
        )

    return render(request, 'shop/search.html', {
        'query': query,
        'products': products,
    })


# Authentication views
def register_view(request):
    """Регистрация"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cart.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'shop/register.html', {'form': form})


def login_view(request):
    """Вход"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            Cart.objects.get_or_create(user=user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'shop/login.html', {'form': form})


def logout_view(request):
    """Выход"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')


# Cart views
@login_required
def cart_view(request):
    """Страница корзины"""
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})


@login_required
@require_POST
def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id, available=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items(),
            'message': f'{product.name} добавлен в корзину'
        })

    messages.success(request, f'{product.name} добавлен в корзину')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


@login_required
@require_POST
def update_cart_item(request, item_id):
    """Обновление количества товара в корзине"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = cart_item.cart
        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items(),
            'cart_total': float(cart.get_total_price()),
            'item_total': float(cart_item.get_total_price()) if quantity > 0 else 0
        })

    return redirect('cart')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items(),
            'cart_total': float(cart.get_total_price()),
            'message': f'{product_name} удален из корзины'
        })

    messages.success(request, f'{product_name} удален из корзины')
    return redirect('cart')


# Order views
@login_required
def checkout(request):
    """Оформление заказа"""
    cart = get_object_or_404(Cart, user=request.user)

    if not cart.items.exists():
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.get_total_price()
            order.save()

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity
                )
                # Update stock
                item.product.stock -= item.quantity
                item.product.save()

            cart.items.all().delete()

            messages.success(request, f'Заказ #{order.id} успешно оформлен!')
            return redirect('order_detail', order_id=order.id)
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = OrderForm(initial=initial)

    return render(request, 'shop/checkout.html', {
        'cart': cart,
        'form': form,
    })


@login_required
def order_list(request):
    """Список заказов пользователя"""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'shop/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


# Wishlist views
@login_required
def wishlist_view(request):
    """Страница избранного"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    """Добавление/удаление из избранного"""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        wishlist_item.delete()
        message = f'{product.name} удален из избранного'
        in_wishlist = False
    else:
        message = f'{product.name} добавлен в избранное'
        in_wishlist = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'in_wishlist': in_wishlist,
            'message': message
        })

    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


@login_required
def profile_view(request):
    """Профиль пользователя"""
    orders = Order.objects.filter(user=request.user)[:5]
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    return render(request, 'shop/profile.html', {
        'orders': orders,
        'wishlist_count': wishlist_count,
    })
