from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.get_inventory, name='get_inventory'),  
    path('search/', views.search_books, name='search_books'),   
    path('authors/', views.get_authors, name='get_authors'),   
    path('addbooks/', views.add_books, name='add_books'),
    path('addauthors/', views.add_authors, name='add_authors'),
    path('update_book/', views.update_book, name='update_book'),  
    path('delete_book/', views.delete_book, name='delete_book'),
]
