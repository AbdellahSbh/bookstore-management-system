from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from .models import Book
from .models import Author


# Create a view to return the entire inventory as JSON
def sort_inventory(request):
    Title = request.GET.get('title', '')
    Price = request.GET.get('price','')
    if Price == 'Desc':
        Descprice = serializers.serialize('json', Book.objects.order_by('-price'))
        return JsonResponse(Descprice, safe=False)
    if Price == 'Asc':
        Ascprice = serializers.serialize('json', Book.objects.order_by('price'))
        return JsonResponse(Ascprice, safe=False)
    if Title == 'AtoZ':
        atoz = serializers.serialize('json', Book.objects.order_by('title'))
        return JsonResponse(atoz, safe=False)
    if Title == 'ZtoA':
        ztoa = serializers.serialize('json', Book.objects.order_by('-title'))
        return JsonResponse(ztoa, safe=False)
    if not Title:
        if not Price:
            books = serializers.serialize('json', Book.objects.all())
            return JsonResponse(books, safe=False)

def search_books(request):
    Author = request.GET.get('author', '').strip()
    Title = request.GET.get('title', '').strip()
    Price = request.GET.get('price', '').strip()

    # Validate input
    if not Author and not Title and not Price:
        return JsonResponse({'error': 'At least one search parameter (author, title, or price) is required.'}, status=400)

    books = Book.objects.all()
    if Author:
        books = books.filter(authors__name__icontains=Author)
    if Title:
        books = books.filter(title__icontains=Title)
    if Price:
        try:
            Price = float(Price)
            books = books.filter(price=Price)
        except ValueError:
            return JsonResponse({'error': 'Price must be a valid number.'}, status=400)

    if not books.exists():
        return JsonResponse({'error': 'No books found matching the criteria.'}, status=404)

    data = serializers.serialize('json', books)
    return JsonResponse(data, safe=False)

def get_authors(request):
    authors = Author.objects.all()
    data = [
        {
            "id": author.id,
            "name": author.name,
            "bio": author.bio
        }
        for author in authors
    ]
    return JsonResponse(data, safe=False)

def add_authors(request):
    name = request.GET.get('name', '')
    bio = request.GET.get('bio', '')
    if not name:
        return JsonResponse({"error": "Author name is required."}, status=400)

    try:
        author, created = Author.objects.get_or_create(name=name, defaults={"bio": bio})
        return JsonResponse({
            "message": "Author created successfully!" if created else "Author already exists.",
            "author": {
                "id": author.id,
                "name": author.name,
                "bio": author.bio,
            }
        }, status=201 if created else 200)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

def add_books(request):
    Title = request.GET.get('title', '').strip()
    Authors = request.GET.get('authors', '').strip()
    Price = request.GET.get('price', '').strip()
    Stock_quantity = request.GET.get('stock', '').strip()

    if not Title:
        return JsonResponse({'error': 'Book title is required.'}, status=400)
    if not Authors:
        return JsonResponse({'error': 'At least one author is required.'}, status=400)
    if not Price:
        return JsonResponse({'error': 'Price is required.'}, status=400)
    if not Stock_quantity:
        return JsonResponse({'error': 'Stock quantity is required.'}, status=400)

    try:
        Price = float(Price)
        if Price <= 0:
            return JsonResponse({'error': 'Price must be a positive number.'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Price must be a valid number.'}, status=400)

    try:
        Stock_quantity = int(Stock_quantity)
        if Stock_quantity < 0:
            return JsonResponse({'error': 'Stock quantity must be a non-negative integer.'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Stock quantity must be a valid integer.'}, status=400)

    if Book.objects.filter(title=Title).exists():
        return JsonResponse({'error': 'A book with this title already exists.'}, status=400)

    author_names = [author_name.strip() for author_name in Authors.split(',')]
    author_objects = Author.objects.filter(name__in=author_names)
    if len(author_objects) != len(author_names):
        return JsonResponse({'error': 'Some authors were not found.'}, status=404)

    book = Book.objects.create(title=Title, price=Price, stock_quantity=Stock_quantity)
    book.authors.set(author_objects)

    return JsonResponse({
        'message': 'Book added successfully!',
        'book': {
            'title': book.title,
            'authors': [author.name for author in book.authors.all()],
            'price': book.price,
            'stock_quantity': book.stock_quantity,
        }
    }, status=201)

def delete_book(request):
    Title = request.GET.get('title', '').strip()

    if not Title:
        return JsonResponse({'error': 'Book title is required to delete the book.'}, status=400)

    try:
        book = get_object_or_404(Book, title=Title)
    except:
        return JsonResponse({'error': 'No book found with the provided title.'}, status=404)

    book.delete()
    return JsonResponse({'message': f"Book '{Title}' deleted successfully!"}, status=200)
def update_book(request):
    title = request.GET.get('title', '')
    new_title = request.GET.get('new_title', '')
    price = request.GET.get('price', '')
    stock_quantity = request.GET.get('stock', '')

    if not title:
        return JsonResponse({"error": "Current book title is required to identify the book."}, status=400)

    book = Book.objects.filter(title=title).first()
    if not book:
        return JsonResponse({"error": f"Book with title '{title}' does not exist."}, status=404)
    if new_title:
        book.title = new_title
    if price:
        try:
            book.price = float(price)
        except ValueError:
            return JsonResponse({"error": "Price must be a valid number."}, status=400)
    if stock_quantity:
        try:
            book.stock_quantity = int(stock_quantity)
        except ValueError:
            return JsonResponse({"error": "Stock quantity must be a valid integer."}, status=400)

    book.save()
    return JsonResponse({
        "message": f"Book '{title}' updated successfully!",
        "updated_fields": {
            "title": book.title,
            "price": book.price,
            "stock_quantity": book.stock_quantity
        }
    }, status=200)
