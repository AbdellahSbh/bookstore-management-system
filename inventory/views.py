from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
from .models import Book
from .models import Author


# Create a view to return the entire inventory as JSON
def get_inventory(request):
    books = Book.objects.all()
    data = serializers.serialize('json', books)
    return JsonResponse(data, safe=False)

def search_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(title__icontains=query)
    data = serializers.serialize('json', books)
    return JsonResponse(data, safe=False)
def get_authors(request):
    authors = Author.objects.all()
    data = serializers.serialize('json', authors)
    return JsonResponse(data, safe=False)