from django.test import TestCase

from unittest.mock import patch
from django.test import TestCase
from .models import Product

class LookupTests(TestCase):
    def setUp(self):
        Product.objects.create(name="Napój mleczny")
        Product.objects.create(name="Mleko")
        Product.objects.create(name="Ptasie Mleczko")

    @patch("products.views.fetch_product_info", return_value={"product_name" : "Mleko WYPASIONE 1L"})
    def test_match(self, _):
        r = self.client.get("/api/products/lookup/", {"ean": "3017620422003"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["matches"]), 1)
        print(r.json()["matches"])

    def test_invalid_ean(self):
        r = self.client.get("/api/products/lookup/", {"ean": "abc"})
        self.assertEqual(r.status_code, 400)

    @patch("products.views.fetch_product_info", return_value=None)
    def test_not_found(self, _):
        r = self.client.get("/api/products/lookup/", {"ean": "12345678"})
        self.assertEqual(r.status_code, 404)
