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
    Author = request.GET.get('author','')
    Title = request.GET.get('title', '')
    Price = request.GET.get('price','')
    if Author:
        byauthor = serializers.serialize('json', Book.objects.filter(authors__name__icontains=Author))
        return JsonResponse(byauthor, safe=False)
    if Title:
        bytitle = serializers.serialize('json', Book.objects.filter(title__icontains=Title))
        return JsonResponse(bytitle, safe=False)
    if Price:
        byprice = serializers.serialize('json', Book.objects.filter(price=Price))
        return JsonResponse(byprice, safe=False)


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
    title = request.GET.get('title', '')
    author_ids = request.GET.get('authors', '')  
    price = request.GET.get('price', '')
    stock_quantity = request.GET.get('stock', '')

    if not title or not author_ids or not price or not stock_quantity:
        return JsonResponse({"error": "All fields (title, authors, price, stock) are required."}, status=400)

    try:
        author_ids = [int(id.strip()) for id in author_ids.split(',')]
    except ValueError:
        return JsonResponse({"error": "Author IDs must be valid integers."}, status=400)

    # Fetch authors
    author_objects = Author.objects.filter(id__in=author_ids)
    if len(author_objects) != len(author_ids):
        return JsonResponse({"error": "One or more author IDs are invalid."}, status=404)

    # Create the book
    try:
        book = Book.objects.create(title=title, price=price, stock_quantity=stock_quantity)
        book.authors.set(author_objects)  # Assign authors to the book
        return JsonResponse({
            "message": "Book added successfully!",
            "book": {
                "title": book.title,
                "authors": [author.name for author in book.authors.all()],
                "price": book.price,
                "stock_quantity": book.stock_quantity,
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

def delete_book(request):
    title = request.GET.get('title', '')
    if not title:
        return JsonResponse({"error": "Book title is required to delete the book."}, status=400)
    
    # Check if the book exists and delete it
    book = Book.objects.filter(title=title).first()
    if not book:
        return JsonResponse({"error": f"Book with title '{title}' does not exist."}, status=404)
    
    book.delete()
    return JsonResponse({"message": f"Book '{title}' deleted successfully!"}, status=200)
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
