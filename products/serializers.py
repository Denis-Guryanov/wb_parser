from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'discounted_price', 'rating', 'reviews_count',
            'session_id', 'created_at', 'image_url', 'wb_url'
        ] 