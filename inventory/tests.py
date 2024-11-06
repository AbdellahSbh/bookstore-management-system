from django.test import TestCase
# inventory/test.py
import unittest
import json
from django.test import Client
from django.urls import reverse

class SimpleInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client()  # Set up the Django test client

    def test_get_inventory(self):
        # Test that the get_inventory endpoint returns a JSON response
        response = self.client.get(reverse('get_inventory'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_search_books(self):
        # Test that the search_books endpoint can be called without errors
        response = self.client.get(reverse('search_books') + '?q=test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_get_authors(self):
        # Test that the get_authors endpoint returns JSON
        response = self.client.get(reverse('get_authors'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
# Create your tests here.
