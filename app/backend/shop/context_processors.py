from .models import Cart, Category


def cart_count(request):
    """Добавляет количество товаров в корзине в контекст"""
    count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.get_total_items()
        except Cart.DoesNotExist:
            pass
    return {'cart_count': count}


def categories(request):
    """Добавляет список категорий в контекст"""
    return {'all_categories': Category.objects.all()}
