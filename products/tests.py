from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product
from django.core.management import call_command
from io import StringIO
import uuid

class ProductModelTest(TestCase):
    """Тесты для модели Product"""
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            price=1000,
            discounted_price=900,
            rating=4.5,
            reviews_count=10,
            session_id=str(uuid.uuid4()),
            image_url="http://example.com/img.jpg",
            wb_url="http://wildberries.ru/product/1"
        )

    def test_str(self):
        self.assertEqual(str(self.product), "Test Product")

    def test_fields(self):
        self.assertEqual(self.product.price, 1000)
        self.assertEqual(self.product.discounted_price, 900)
        self.assertEqual(self.product.rating, 4.5)
        self.assertEqual(self.product.reviews_count, 10)
        self.assertTrue(self.product.session_id)
        self.assertTrue(self.product.created_at)
        self.assertEqual(self.product.image_url, "http://example.com/img.jpg")
        self.assertEqual(self.product.wb_url, "http://wildberries.ru/product/1")

class ProductAPITest(TestCase):
    """Тесты для ProductViewSet и связанных API"""
    def setUp(self):
        self.client = APIClient()
        self.session_id = str(uuid.uuid4())
        self.product = Product.objects.create(
            name="API Product",
            price=2000,
            discounted_price=1500,
            rating=4.0,
            reviews_count=5,
            session_id=self.session_id,
            image_url="http://example.com/api.jpg",
            wb_url="http://wildberries.ru/product/2"
        )

    def test_list_products_with_session_id(self):
        url = reverse('product-list')
        response = self.client.get(url, {'session_id': self.session_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "API Product")

    def test_list_products_without_session_id(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filter_by_min_price(self):
        url = reverse('product-list')
        response = self.client.get(url, {'session_id': self.session_id, 'min_price': 1000})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(url, {'session_id': self.session_id, 'min_price': 3000})
        self.assertEqual(len(response.data), 0)

    def test_filter_by_min_rating(self):
        url = reverse('product-list')
        response = self.client.get(url, {'session_id': self.session_id, 'min_rating': 4.5})
        self.assertEqual(len(response.data), 0)
        response = self.client.get(url, {'session_id': self.session_id, 'min_rating': 4.0})
        self.assertEqual(len(response.data), 1)

    def test_filter_by_min_reviews(self):
        url = reverse('product-list')
        response = self.client.get(url, {'session_id': self.session_id, 'min_reviews_count': 10})
        self.assertEqual(len(response.data), 0)
        response = self.client.get(url, {'session_id': self.session_id, 'min_reviews_count': 5})
        self.assertEqual(len(response.data), 1)

    def test_get_session_products(self):
        url = reverse('product-get-session-products')
        response = self.client.get(url, {'session_id': self.session_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['session_id'], self.session_id)
        self.assertEqual(data['count'], 1)

    def test_clear_session(self):
        url = reverse('product-clear-session')
        response = self.client.post(url, {'session_id': self.session_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.filter(session_id=self.session_id).count(), 0)

    def test_parse_product_requires_url_and_session_id(self):
        url = reverse('product-parse-product')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, {'url': 'http://wildberries.ru'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, {'session_id': self.session_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parse_search_requires_query_and_session_id(self):
        url = reverse('product-parse-search')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, {'query': 'test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(url, {'session_id': self.session_id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ParseWbCommandTest(TestCase):
    """Тесты для management-команды parse_wb"""
    def test_command_runs_and_handles_no_products(self):
        out = StringIO()
        call_command('parse_wb', 'unlikelysearchquery', session_id=str(uuid.uuid4()), stdout=out)
        self.assertIn('No products found.', out.getvalue())

    def test_command_runs_and_creates_products(self):
        # Для настоящего парсинга нужен реальный ответ от WB, поэтому тест может быть нестабильным.
        # Здесь пример вызова команды, но для стабильности стоит мокать requests.get.
        out = StringIO()
        call_command('parse_wb', 'носки', session_id=str(uuid.uuid4()), stdout=out)
        self.assertIn('Parsing finished.', out.getvalue())
