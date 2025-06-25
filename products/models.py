from django.db import models
import uuid

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    discounted_price = models.IntegerField()
    rating = models.FloatField()
    reviews_count = models.IntegerField()
    session_id = models.CharField(max_length=36, blank=True, null=True, help_text="ID сессии парсинга")
    created_at = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(blank=True, null=True, help_text="URL изображения товара")
    wb_url = models.URLField(blank=True, null=True, help_text="Ссылка на товар на Wildberries")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
