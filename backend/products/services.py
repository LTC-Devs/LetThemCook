import os
import requests

from .models import Product

from django.contrib.postgres.search import TrigramSimilarity

OFF_URL = "https://world.openfoodfacts.org/api/v3/product/{ean}.json"
# For User-Agent identification required by OpenFoodFacts
OFF_USER_CONTACT = os.getenv("USER_CONTACT", "")

def fetch_product_info(ean: str) -> dict | None:
    """Fetches product information: name (pl, en) and keywords"""
    FIELDS = [
        'product_name', 'product_name_pl', 
        'generic_name_pl', 'generic_name',
        'brands',
        'pnns_groups_2', 'categories_tags',
    ]
    fields_str = ','.join(FIELDS)
    resp = requests.get(
        OFF_URL.format(ean=ean),
        params={'fields': fields_str},
        headers={"User-Agent": f"LetThemCook/0.1 {OFF_USER_CONTACT}"},
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "success":
        return None

    product: dict = data.get("product", {})
    result = {
        'product_name': product.get("product_name"), 
        'product_name_pl': product.get('product_name_pl'), 
        'generic_name_pl': product.get('generic_name_pl'), 
        'generic_name': product.get('generic_name'),
        'brands': product.get('brands'),
        'pnns_groups_2': product.get('pnns_groups_2'), 
        'categories_tags': product.get('categories_tags'),
    }
    return result

def _build_product_search_str(product: dict) -> str:
    if not product:
        return ""
    product_name = product.get("generic_name_pl") or product.get("product_name_pl") or product.get("product_name")
    return product_name

def search_products(product: dict, limit: int = 5):
    """Simple text search"""
    if not product:
        return
    query = _build_product_search_str(product)
    if not query:
        return []
    
    matches = Product.objects.annotate(
            similarity=TrigramSimilarity('name', query)
        ).filter(similarity__gt=0.3).order_by('-similarity')
    return matches[:limit]