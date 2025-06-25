import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Parse products from Wildberries'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='Search query for products')
        parser.add_argument('--session-id', type=str, help='Session ID for grouping products')

    def handle(self, *args, **options):
        query = options['query']
        session_id = options.get('session_id')
        self.stdout.write(self.style.SUCCESS(f'Starting to parse Wildberries for query: {query}'))

        url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&curr=rub&dest=-1257786&query={query}&resultset=catalog&spp=0"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            try:
                data = response.json()
            except ValueError:
                self.stderr.write(self.style.ERROR('Error parsing JSON'))
                self.stderr.write(self.style.ERROR(f'Response text: {response.text}'))
                return

            products_data = data.get('data', {}).get('products', [])
            if not products_data:
                self.stdout.write(self.style.WARNING('No products found.'))
                return

            for item in products_data:
                image_url = None
                if item.get('pics') and isinstance(item['pics'], list) and item['pics']:
                    image_url = f"https://images.wbstatic.net/c516x688/{item['pics'][0]}.jpg"
                wb_url = f"https://www.wildberries.ru/catalog/{item.get('id')}/detail.aspx" if item.get('id') else None
                Product.objects.create(
                    name=item.get('name'),
                    price=item.get('priceU') // 100 if item.get('priceU') else 0,
                    discounted_price=item.get('salePriceU') // 100 if item.get('salePriceU') else 0,
                    rating=item.get('rating'),
                    reviews_count=item.get('feedbacks'),
                    session_id=session_id,
                    image_url=image_url,
                    wb_url=wb_url,
                )
            self.stdout.write(self.style.SUCCESS(f'Successfully parsed {len(products_data)} products.'))

        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error while requesting data: {e}'))
        except ValueError as e:
            self.stderr.write(self.style.ERROR(f'Error parsing JSON: {e}'))

        self.stdout.write(self.style.SUCCESS('Parsing finished.')) 