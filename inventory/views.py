from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
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

def add_authors(request):
    Name = request.GET.get('name', '')
    Bio = request.GET.get('bio', '')
    author = Author.create(name=Name, bio=Bio)
    return JsonResponse({'name': author.name, 'bio': author.bio})

def add_books(request):
        Title = request.GET.get('title', '')
        Authors = request.GET.get('authors','')
        Price = request.GET.get('price','')
        Stock_quantity = request.GET.get('stock','')
        author_names = [author_name.strip() for author_name in Authors.split(',')] if Authors else[]
        author_objects = Author.objects.filter(name__in=author_names)
        if len(author_objects) != len(author_names):
                return JsonResponse({'error': 'Author not found.'}, status=404)
        book = Book.create(title=Title, price=Price, stock_quantity=Stock_quantity)
        book.authors.set(author_objects)
        return JsonResponse({'title': book.title, 'authors': [author.name for author in book.authors.all()], 'price': book.price, 'stock': book.stock_quantity})
def delete_book(request):
    Title = request.GET.get('title', '')
    if not Title:
        return JsonResponse({"error": "Book title is required to delete the book."}, status=400)
    book = get_object_or_404(Book, title=Title)
    book.delete() 
    return JsonResponse({"message": f"Book '{Title}' deleted successfully!"}, status=200)
def update_book(request):
    Title = request.GET.get('title', '')
    New_title = request.GET.get('new_title', '')
    Price = request.GET.get('price', '')
    Stock_quantity = request.GET.get('stock', '')
    if not Title:
        return JsonResponse({"error": "Current book title is required to identify the book."}, status=400)
    book = get_object_or_404(Book, title=Title)
    if New_title:
        book.title = New_title
    if Price:
        book.price = Price
    if Stock_quantity:
        book.stock_quantity = Stock_quantity
    book.save()
    return JsonResponse({
        "message": "Book updated successfully!",
        "updated_fields": {
            "title": book.title,
            "price": book.price,
            "stock_quantity": book.stock_quantity
        }
    }, status=200)
