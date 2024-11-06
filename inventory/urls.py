from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.get_inventory, name='get_inventory'),  # Get all books as JSON
    path('search/', views.search_books, name='search_books'),   # Search for books as JSON
    path('authors/', views.get_authors, name='get_authors'),         # Get all authors as JSON
]