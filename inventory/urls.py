from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.sort_inventory, name='sort_inventory'),  
    path('search/', views.search_books, name='search_books'),   
    path('authors/', views.get_authors, name='get_authors'),   
    path('addbooks/', views.add_books, name='add_books'),
    path('addauthors/', views.add_authors, name='add_authors'),
    path('update_book/', views.update_book, name='update_book'),  
    path('delete_book/', views.delete_book, name='delete_book'),
    path('fetch_google_books/', views.fetch_books_from_google, name='fetch_google_books'),
    path('fetch_and_add_book/', views.fetch_and_add_book, name='fetch_and_add_book'),
    path('bulk_add_books/', views.bulk_add_books, name='bulk_add_books'),
    path('bulk_delete_books/', views.bulk_delete_books, name='bulk_delete_books'),
]
