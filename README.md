# Wildberries Parser

Веб-приложение для парсинга и анализа товаров с Wildberries.

## Возможности

- **Парсинг конкретного товара** - введите URL товара с Wildberries для получения информации
- **Парсинг по поисковому запросу** - найдите товары по ключевым словам
- **Фильтрация товаров** - фильтруйте по цене, рейтингу и количеству отзывов
- **Сортировка** - сортируйте товары по любому столбцу
- **Аналитика** - графики распределения цен и зависимости скидки от рейтинга

## Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd wb_parser
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate  # Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Примените миграции:**
   ```bash
   python manage.py migrate
   ```

5. **Запустите сервер:**
   ```bash
   python manage.py runserver
   ```

6. **Откройте браузер:**
   ```
   http://127.0.0.1:8000/
   ```

## Использование

### Парсинг конкретного товара
1. Скопируйте URL товара с Wildberries (например: `https://www.wildberries.ru/catalog/12345678/detail.aspx`)
2. Вставьте URL в поле "Парсинг конкретного товара"
3. Нажмите "Спарсить товар"

### Парсинг по поисковому запросу
1. Введите поисковый запрос (например: "кроссовки", "телефон")
2. Нажмите "Найти товары"

### Фильтрация
- Используйте слайдер цены для фильтрации по минимальной цене
- Введите минимальный рейтинг (0-5)
- Введите минимальное количество отзывов
- Нажмите "Сбросить фильтры" для очистки

### Сортировка
- Кликните на заголовок столбца для сортировки
- Повторный клик изменит направление сортировки

## API Endpoints

- `GET /api/products/` - получить все товары
- `POST /api/products/parse_product/` - спарсить конкретный товар
- `POST /api/products/parse_search/` - спарсить товары по запросу

### Примеры API запросов

**Парсинг товара:**
```bash
curl -X POST http://127.0.0.1:8000/api/products/parse_product/ \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.wildberries.ru/catalog/12345678/detail.aspx"}'
```

**Парсинг по запросу:**
```bash
curl -X POST http://127.0.0.1:8000/api/products/parse_search/ \
  -H "Content-Type: application/json" \
  -d '{"query":"кроссовки"}'
```

## Технологии

- **Backend:** Django 5.2.3, Django REST Framework
- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **Графики:** Chart.js
- **Парсинг:** requests, BeautifulSoup4
- **База данных:** SQLite

## Структура проекта

```
wb_parser/
├── frontend/          # Статические файлы (CSS, JS)
├── templates/         # HTML шаблоны
├── products/          # Django приложение
│   ├── models.py      # Модели данных
│   ├── views.py       # API представления
│   ├── urls.py        # URL маршруты
│   └── management/    # Команды управления
├── wb_parser/         # Настройки Django
├── manage.py          # Управление Django
└── requirements.txt   # Зависимости Python
```

## Лицензия

MIT License 