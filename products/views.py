from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.management import call_command
from django.core.management.base import CommandError
import requests
from bs4 import BeautifulSoup
import re
import uuid
from .models import Product
from .serializers import ProductSerializer

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        session_id = self.request.query_params.get('session_id')
        min_price = self.request.query_params.get('min_price')
        min_rating = self.request.query_params.get('min_rating')
        min_reviews = self.request.query_params.get('min_reviews_count')

        # По умолчанию показываем только товары с session_id
        # Если session_id не указан, возвращаем пустой queryset
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        else:
            # Если session_id не указан, возвращаем пустой список
            return Product.objects.none()
        
        if min_price:
            queryset = queryset.filter(discounted_price__gte=min_price)
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        if min_reviews:
            queryset = queryset.filter(reviews_count__gte=min_reviews)

        return queryset

    @action(detail=False, methods=['post'])
    def parse_product(self, request):
        """Парсинг конкретного товара по URL"""
        url = request.data.get('url')
        session_id = request.data.get('session_id')
        
        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Извлекаем ID товара из URL Wildberries
            product_id_match = re.search(r'/catalog/(\d+)/', url)
            if not product_id_match:
                return Response({'error': 'Invalid Wildberries URL'}, status=status.HTTP_400_BAD_REQUEST)
            
            product_id = product_id_match.group(1)
            
            # API для получения информации о товаре
            api_url = f"https://card.wb.ru/cards/detail?nm={product_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            products_data = data.get('data', {}).get('products', [])
            if not products_data:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
            product_data = products_data[0]
            
            # Создаем или обновляем товар с session_id
            image_url = None
            if product_data.get('pics') and isinstance(product_data['pics'], list) and product_data['pics']:
                image_url = f"https://images.wbstatic.net/c516x688/{product_data['pics'][0]}.jpg"
            wb_url = f"https://www.wildberries.ru/catalog/{product_data.get('id')}/detail.aspx" if product_data.get('id') else url
            product, created = Product.objects.update_or_create(
                name=product_data.get('name'),
                session_id=session_id,
                defaults={
                    'price': product_data.get('priceU') // 100 if product_data.get('priceU') else 0,
                    'discounted_price': product_data.get('salePriceU') // 100 if product_data.get('salePriceU') else 0,
                    'rating': product_data.get('rating'),
                    'reviews_count': product_data.get('feedbacks'),
                    'image_url': image_url,
                    'wb_url': wb_url,
                }
            )
            
            serializer = self.get_serializer(product)
            return Response({
                'message': 'Product parsed successfully' if created else 'Product updated successfully',
                'product': serializer.data,
                'session_id': session_id
            }, status=status.HTTP_200_OK)
            
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Error fetching product data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def parse_search(self, request):
        """Парсинг товаров по поисковому запросу"""
        query = request.data.get('query')
        session_id = request.data.get('session_id')
        
        if not query:
            return Response({'error': 'Query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Используем обновленную команду для парсинга с session_id
            call_command('parse_wb', query, session_id=session_id)
            
            # Возвращаем товары с session_id
            session_products = Product.objects.filter(session_id=session_id).order_by('-created_at')
            serializer = self.get_serializer(session_products, many=True)
            
            return Response({
                'message': f'Successfully parsed products for query: {query}',
                'products': serializer.data,
                'session_id': session_id
            }, status=status.HTTP_200_OK)
            
        except CommandError as e:
            return Response({'error': f'Error parsing products: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def get_session_products(self, request):
        """Получить товары конкретной сессии"""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(session_id=session_id).order_by('-created_at')
        serializer = self.get_serializer(products, many=True)
        
        return Response({
            'products': serializer.data,
            'session_id': session_id,
            'count': products.count()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def clear_session(self, request):
        """Очистить товары конкретной сессии"""
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count = Product.objects.filter(session_id=session_id).delete()[0]
        
        return Response({
            'message': f'Successfully deleted {deleted_count} products from session',
            'session_id': session_id
        }, status=status.HTTP_200_OK)
