
# 🛒 ShopMarket

[![Django CI](https://github.com/GVia93/MarketShop/actions/workflows/django-ci.yml/badge.svg)](https://github.com/GVia93/MarketShop/actions/workflows/django-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.x](https://img.shields.io/badge/django-5.x-green.svg)](https://www.djangoproject.com/)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Современный интернет-магазин на Django с полным функционалом электронной коммерции.

![ShopMarket Preview](https://via.placeholder.com/800x400/2563eb/ffffff?text=ShopMarket)

## ✨ Возможности

- 🛍️ **Каталог товаров** — категории, фильтрация, поиск
- 🛒 **Корзина** — добавление, удаление, изменение количества (AJAX)
- ❤️ **Избранное** — список желаний для авторизованных пользователей
- 📦 **Заказы** — оформление, история, отслеживание статуса
- 👤 **Личный кабинет** — профиль, история заказов
- 🔐 **Аутентификация** — регистрация, вход, выход
- 🛠️ **Админ-панель** — полное управление магазином

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- pip

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/GVia93/MarketShop.git
cd MarketShop

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Перейти в директорию backend
cd app/backend

# Создать файл .env
cat > .env << EOF
SECRET_KEY=your-secret-key-here
DEBUG=True
EOF

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

Откройте http://localhost:8000 в браузере.

### Загрузка тестовых данных

```bash
python manage.py shell << 'EOF'
from shop.models import Category, Product

# Создание категорий
Category.objects.create(name='Электроника', slug='elektronika', description='Техника и гаджеты')
Category.objects.create(name='Одежда', slug='odezhda', description='Мужская и женская одежда')
Category.objects.create(name='Книги', slug='knigi', description='Литература')

# Создание товаров
cat = Category.objects.get(slug='elektronika')
Product.objects.create(category=cat, name='iPhone 15', slug='iphone-15', description='Смартфон Apple', price=89990, stock=10)
Product.objects.create(category=cat, name='MacBook Pro', slug='macbook-pro', description='Ноутбук Apple', price=199990, stock=5)

print('Тестовые данные загружены!')
EOF
```

## 📁 Структура проекта

```
MarketShop/
├── .github/
│   └── workflows/
│       └── django-ci.yml    # CI/CD конфигурация
├── app/
│   └── backend/
│       ├── config/          # Настройки Django
│       │   ├── settings.py
│       │   ├── urls.py
│       │   └── wsgi.py
│       ├── shop/            # Основное приложение
│       │   ├── models.py    # Модели данных
│       │   ├── views.py     # Представления
│       │   ├── forms.py     # Формы
│       │   ├── urls.py      # URL маршруты
│       │   ├── admin.py     # Админ-панель
│       │   └── tests.py     # Тесты (55 тестов)
│       ├── templates/       # HTML шаблоны
│       │   ├── base.html
│       │   └── shop/
│       ├── static/          # Статические файлы
│       ├── media/           # Загруженные файлы
│       └── manage.py
└── requirements.txt
```

## 🗄️ Модели данных

| Модель | Описание |
|--------|----------|
| `Category` | Категории товаров |
| `Product` | Товары с ценой, описанием, остатком |
| `Cart` | Корзина пользователя |
| `CartItem` | Элемент корзины |
| `Order` | Заказ с данными доставки |
| `OrderItem` | Элемент заказа |
| `Wishlist` | Избранные товары |

## 🔗 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Главная страница |
| GET | `/products/` | Каталог товаров |
| GET | `/product/<slug>/` | Детали товара |
| GET | `/category/<slug>/` | Товары категории |
| GET | `/search/?q=` | Поиск товаров |
| GET | `/cart/` | Корзина |
| POST | `/cart/add/<id>/` | Добавить в корзину |
| POST | `/cart/update/<id>/` | Обновить количество |
| POST | `/cart/remove/<id>/` | Удалить из корзины |
| GET | `/checkout/` | Оформление заказа |
| POST | `/checkout/` | Создать заказ |
| GET | `/orders/` | История заказов |
| GET | `/order/<id>/` | Детали заказа |
| GET | `/wishlist/` | Избранное |
| POST | `/wishlist/toggle/<id>/` | Добавить/удалить из избранного |
| GET | `/profile/` | Профиль пользователя |
| GET/POST | `/login/` | Вход |
| GET/POST | `/register/` | Регистрация |
| GET/POST | `/logout/` | Выход |

## 🧪 Тестирование

```bash
# Запуск всех тестов
python manage.py test shop

# Запуск с подробным выводом
python manage.py test shop --verbosity=2

# Запуск с покрытием кода
pip install coverage
coverage run --source='shop' manage.py test shop
coverage report -m
coverage html  # HTML отчёт в htmlcov/
```

### Покрытие тестами: 94%

- ✅ Модели (Category, Product, Cart, Order, Wishlist)
- ✅ Формы (RegisterForm, OrderForm, SearchForm)
- ✅ Views (все страницы и действия)
- ✅ Аутентификация
- ✅ Транзакции и проверка stock

## 🔄 CI/CD

Проект использует GitHub Actions для автоматизации:

| Workflow | Описание |
|----------|----------|
| **test** | Тесты на Python 3.11 и 3.12 |
| **lint** | Проверка кода (Ruff) |
| **security** | Сканирование уязвимостей (Bandit, Safety) |

CI запускается автоматически при push/PR в ветки `develop`, `master`, `main`.

## ⚙️ Конфигурация

### Переменные окружения (.env)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `SECRET_KEY` | Секретный ключ Django | **обязательно** |
| `DEBUG` | Режим отладки | `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Доверенные источники | `http://localhost:8001` |

### Генерация SECRET_KEY

```bash
python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"
```

## 🛡️ Безопасность

В production режиме автоматически включаются:

- ✅ CSRF защита
- ✅ XSS фильтр
- ✅ Secure cookies
- ✅ X-Frame-Options: DENY
- ✅ Content-Type nosniff

## 📦 Зависимости

| Пакет | Версия | Назначение |
|-------|--------|------------|
| Django | 5.x | Веб-фреймворк |
| django-crispy-forms | 2.x | Красивые формы |
| crispy-bootstrap5 | 2025.x | Bootstrap 5 для форм |
| django-environ | 0.13.x | Переменные окружения |
| Pillow | 12.x | Работа с изображениями |

## 🚀 Деплой

### Docker (рекомендуется)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/backend .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD [\"gunicorn\", \"config.wsgi:application\", \"--bind\", \"0.0.0.0:8000\"]
```

### Gunicorn + Nginx

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## 🤝 Участие в разработке

1. Fork репозитория
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменений (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT License — см. [LICENSE](LICENSE) файл.

## 👤 Автор

**GVia93** — [GitHub](https://github.com/GVia93)

---
